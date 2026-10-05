import json
import logging
import re

from groq import Groq, GroqError, RateLimitError
from pydantic import ValidationError

from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.schemas.cv import TailoredCV
from app.services.skill_taxonomy import SKILL_TAXONOMY, extract_taxonomy_skills

logger = logging.getLogger(__name__)

# Groq's free tier allows 8,000 tokens/minute, so inputs are capped to keep one
# generation around 2-3k tokens.
MAX_RESUME_CHARS = 8000
MAX_JD_CHARS = 5000
MAX_COMPLETION_TOKENS = 3000
MAX_KEYWORDS = 25

_ALIAS_TO_SKILL = {
    term.lower(): name
    for name, (aliases, _) in SKILL_TAXONOMY.items()
    for term in [name, *aliases]
}

# Umbrella skills a candidate can honestly claim when they have a specific child skill.
IMPLIED_BY = {
    "Machine Learning": {"PyTorch", "TensorFlow", "Scikit-learn", "Deep Learning"},
    "SQL": {"PostgreSQL"},
    "REST APIs": {"FastAPI", "Django", "Flask", "Spring Boot"},
}

SYSTEM_PROMPT = """You rewrite resumes so they pass applicant tracking systems (ATS) for one specific job.

Hard rules:
- Use ONLY facts present in the original resume. Never invent employers, job titles, dates,
  degrees, certifications, metrics, numbers, or skills.
- First decide jd_keywords. Then, for every keyword the original resume genuinely supports
  (directly, or as the standard umbrella term - e.g. training PyTorch or Scikit-learn models
  supports "Machine Learning"; FastAPI work supports "REST APIs"), make sure that exact
  keyword appears in the summary, the skills list, or a bullet.
- Rewrite every bullet - do not copy them verbatim. Lead with the part most relevant to this
  job, start with a strong action verb, and use the job's terminology where it is truthful.
  Keep numbers that exist in the original; never add new ones.
- Never mention a technology the original resume does not support, even inside a bullet.
- skills: only skills the original resume supports, most relevant to this job first.
- headline: the candidate's real role, phrased toward the target job (no seniority they lack).
- summary: 2-3 sentences aimed at this job, grounded in the original resume.
- Leave a field empty or null when the original resume does not contain it.

Return a single JSON object with exactly these keys:
{
  "jd_keywords": [up to 25 short skills, tools, or qualifications the job asks for, using the job's wording],
  "cv": {
    "full_name": str, "headline": str, "email": str|null, "phone": str|null,
    "location": str|null, "links": [str], "summary": str, "skills": [str],
    "experience": [{"role": str, "company": str, "location": str|null,
                    "start": str|null, "end": str|null, "bullets": [str]}],
    "projects": [{"name": str, "bullets": [str]}],
    "education": [{"degree": str, "institution": str, "year": str|null, "details": str|null}],
    "certifications": [str]
  }
}"""


class CVTailorError(RuntimeError):
    pass


class CVTailorBusyError(CVTailorError):
    pass


def _phrase_pattern(phrase: str) -> re.Pattern:
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(phrase)}(?![A-Za-z0-9])", re.IGNORECASE)


def contains_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.strip()
    return bool(phrase) and bool(_phrase_pattern(phrase).search(text))


def mentions_skill(text: str, skill: str) -> bool:
    canonical = _ALIAS_TO_SKILL.get(skill.strip().lower())
    if canonical:
        return canonical in extract_taxonomy_skills(text)
    return contains_phrase(text, skill)


def skill_is_evidenced(skill: str, original_text: str) -> bool:
    if mentions_skill(original_text, skill):
        return True
    canonical = _ALIAS_TO_SKILL.get(skill.strip().lower())
    return bool(canonical and IMPLIED_BY.get(canonical, set()) & extract_taxonomy_skills(original_text))


def filter_skills(skills: list[str], original_text: str) -> tuple[list[str], list[str]]:
    kept, removed, seen = [], [], set()
    for skill in skills:
        key = skill.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        (kept if skill_is_evidenced(skill, original_text) else removed).append(skill.strip())
    return kept, removed


def merge_keywords(llm_keywords: list[str], job_description: str) -> list[str]:
    merged, seen = [], set()
    for keyword in [*sorted(extract_taxonomy_skills(job_description)), *llm_keywords]:
        key = keyword.strip().lower()
        if key and key not in seen and len(key) <= 60:
            seen.add(key)
            merged.append(keyword.strip())
    return merged[:MAX_KEYWORDS]


def keyword_coverage(keywords: list[str], text: str) -> tuple[list[str], float]:
    matched = [k for k in keywords if mentions_skill(text, k)]
    coverage = round(len(matched) / len(keywords), 3) if keywords else 0.0
    return matched, coverage


def cv_to_text(cv: TailoredCV) -> str:
    parts = [cv.full_name, cv.headline, cv.summary, ", ".join(cv.skills), *cv.certifications]
    for job in cv.experience:
        parts += [job.role, job.company, *job.bullets]
    for project in cv.projects:
        parts += [project.name, *project.bullets]
    for edu in cv.education:
        parts += [edu.degree, edu.institution, edu.details or ""]
    return "\n".join(p for p in parts if p)


def enforce_provenance(cv: TailoredCV, original_text: str) -> list[str]:
    """Blank employer/institution names absent from the original; flag new technologies."""
    warnings = []
    for job in cv.experience:
        if job.company and not contains_phrase(original_text, job.company):
            warnings.append(f"Removed employer '{job.company}' - it is not in your original CV.")
            job.company = None
    for edu in cv.education:
        if edu.institution and not contains_phrase(original_text, edu.institution):
            warnings.append(f"Removed institution '{edu.institution}' - it is not in your original CV.")
            edu.institution = None

    original_skills = extract_taxonomy_skills(original_text)
    for skill in sorted(extract_taxonomy_skills(cv_to_text(cv)) - original_skills):
        if not IMPLIED_BY.get(skill, set()) & original_skills:
            warnings.append(f"The tailored CV mentions '{skill}', which is not in your original CV - edit it out unless you really have it.")
    return warnings


def call_llm(resume_text: str, job_title: str, company: str, job_description: str) -> dict:
    if not GROQ_API_KEY:
        raise CVTailorError("GROQ_API_KEY is not configured on the server.")

    user_prompt = (
        f"TARGET JOB: {job_title or 'not given'} at {company or 'not given'}\n\n"
        f"JOB DESCRIPTION:\n{job_description[:MAX_JD_CHARS]}\n\n"
        f"ORIGINAL RESUME:\n{resume_text[:MAX_RESUME_CHARS]}"
    )
    client = Groq(api_key=GROQ_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    options = {"max_completion_tokens": MAX_COMPLETION_TOKENS}
    if GROQ_MODEL.startswith("openai/gpt-oss"):
        options["reasoning_effort"] = "low"

    # Groq's strict JSON mode intermittently rejects valid generations, so fall back to
    # plain mode and extract the JSON object ourselves. Rate limits are not retried:
    # retrying immediately only burns more of the per-minute token budget.
    for json_mode in (True, True, False):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                temperature=0.2,
                messages=messages,
                **options,
                **({"response_format": {"type": "json_object"}} if json_mode else {}),
            )
        except RateLimitError as exc:
            logger.warning("Groq rate limit hit while tailoring CV: %s", exc)
            raise CVTailorBusyError(
                "The AI is busy right now (free-tier rate limit). Please try again in about a minute."
            ) from exc
        except GroqError as exc:
            logger.warning("Groq error while tailoring CV (json_mode=%s): %s", json_mode, exc)
            continue
        parsed = extract_json(response.choices[0].message.content)
        if parsed is not None:
            return parsed

    raise CVTailorError("The AI could not produce a CV right now. Please try again in a moment.")


def extract_json(content: str | None) -> dict | None:
    if not content:
        return None
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(content[start:end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def tailor_cv(resume_text: str, job_title: str, company: str, job_description: str) -> dict:
    payload = call_llm(resume_text, job_title, company, job_description)
    try:
        cv = TailoredCV.model_validate(payload.get("cv") or {})
    except ValidationError as exc:
        raise CVTailorError("The AI returned an incomplete CV. Please try again.") from exc

    cv.skills, removed = filter_skills(cv.skills, resume_text)
    warnings = enforce_provenance(cv, resume_text)

    keywords = merge_keywords(payload.get("jd_keywords") or [], job_description)
    matched_before, coverage_before = keyword_coverage(keywords, resume_text)
    matched_after, coverage_after = keyword_coverage(keywords, cv_to_text(cv))

    return {
        "cv": cv,
        "ats": {
            "keywords": keywords,
            "matched_before": matched_before,
            "matched_after": matched_after,
            "missing": [k for k in keywords if k not in matched_after],
            "coverage_before": coverage_before,
            "coverage_after": coverage_after,
        },
        "removed_skills": removed,
        "warnings": warnings,
    }
