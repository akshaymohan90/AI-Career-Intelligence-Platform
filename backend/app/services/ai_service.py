import os

from groq import Groq

from app.services.career_analysis import analyze_career_fit

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
GROQ_MODEL = "groq/compound"


def build_career_prompt(
    resume_skills: list[str],
    job_skills: list[str]
) -> str:

    analysis = analyze_career_fit(
        resume_skills,
        job_skills
    )

    prompt = f"""
You are an AI career advisor.

Analyze the candidate against the target job.

Candidate skills:
{", ".join(resume_skills)}

Required job skills:
{", ".join(job_skills)}

Match score:
{analysis["match_score"]}%

Matched skills:
{", ".join(analysis["matched_skills"])}

Missing skills:
{", ".join(analysis["missing_skills"])}

Provide:
1. Overall fit assessment
2. Most important skill gaps
3. Recommended learning priorities
4. Practical next steps
"""

    return prompt.strip()


def generate_career_advice(
    resume_skills: list[str],
    job_skills: list[str]
) -> str:
    """Generate realistic AI career advice using Groq when configured; fallback to template logic otherwise."""
    analysis = analyze_career_fit(resume_skills, job_skills)

    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful AI career coach."},
                    {"role": "user", "content": build_career_prompt(resume_skills, job_skills)}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            answer = response.choices[0].message.content
            if answer and answer.strip():
                return answer.strip()
        except Exception as exc:
            raise RuntimeError(f"Groq AI generation failed: {exc}") from exc

    matched = ", ".join(analysis["matched_skills"]) if analysis.get("matched_skills") else "none"
    missing = ", ".join(analysis["missing_skills"]) if analysis.get("missing_skills") else "none"

    return (
        f"Your current profile matches this role at {analysis['match_score']}%. "
        f"Strong matches include: {matched}. "
        f"The main gaps to close are: {missing}. "
        f"Focus on strengthening the missing skills, building a small project around them, "
        f"and tailoring your resume to highlight the matching capabilities."
    )