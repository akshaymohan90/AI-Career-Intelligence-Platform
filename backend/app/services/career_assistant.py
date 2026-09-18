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
You are an AI Career Assistant.

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

Give practical, personalized career advice.

Use the candidate's actual skills and skill gaps.
Use the career knowledge as supporting context.
Do not invent candidate experience.
"""

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional AI career advisor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content