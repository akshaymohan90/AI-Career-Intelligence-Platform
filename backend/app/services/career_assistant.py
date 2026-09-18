from app.services.career_analysis import analyze_career_fit
from app.services.rag_service import retrieve_career_context
from app.core.config import GROQ_API_KEY, GROQ_MODEL
from groq import Groq


def generate_career_assistant_response(
    question: str,
    resume_skills: list[str],
    job_skills: list[str]
) -> str:

    if not GROQ_API_KEY:
        return (
            "The AI career assistant isn't configured yet — set GROQ_API_KEY "
            "to enable this feature."
        )

    analysis = analyze_career_fit(
        resume_skills,
        job_skills
    )

    context = retrieve_career_context(
        question,
        n_results=3
    )

    context_text = "\n\n".join(context)

    prompt = f"""
Candidate skills:
{", ".join(resume_skills)}

Target job skills:
{", ".join(job_skills)}

Match score:
{analysis["match_score"]}%

Matched skills:
{", ".join(analysis["matched_skills"])}

Missing skills:
{", ".join(analysis["missing_skills"])}

Relevant career knowledge:
{context_text}

User question:
{question}

If the user question above is genuinely about this candidate's resume,
this specific job, their skill gap, or their career/professional
development, give practical, personalized career advice — use the
candidate's actual skills and skill gaps, and use the career knowledge
as supporting context. Do not invent candidate experience.

If the user question is NOT about their resume, this job, or their
career/professional development (for example: general knowledge,
unrelated how-to questions, personal advice, or anything outside career
and job-fit topics), do not answer it — even loosely or creatively tying
it back to careers. Instead, reply with exactly:
"I can only help with questions about your resume, this job, and your
career development — try asking something like 'what skill should I
prioritize?' or 'how does my experience compare to this role?'"
"""

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a career assistant scoped strictly to this "
                    "candidate's resume, this job posting, their skill gap, "
                    "and general career/professional development. You must "
                    "refuse — not creatively reinterpret — any question "
                    "outside that scope, using the exact refusal message "
                    "the user prompt specifies."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content