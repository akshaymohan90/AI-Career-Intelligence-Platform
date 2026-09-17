import os

from groq import Groq

from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.services.vector_store import search_documents


def get_groq_client():
    if not GROQ_API_KEY:
        return None

    try:
        return Groq(api_key=GROQ_API_KEY)
    except Exception:
        return None


def retrieve_career_context(
    query: str,
    n_results: int = 3
) -> list[str]:

    result = search_documents(
        query,
        n_results
    )

    return result["documents"][0]


def generate_rag_answer(
    query: str
) -> str:

    context = retrieve_career_context(
        query
    )

    if not context:
        return "I could not find relevant career guidance for that question."

    context_text = "\n\n".join(
        context
    )

    prompt = f"""
You are an AI career advisor.

Use the provided career knowledge to answer
the user's question.

Career knowledge:
{context_text}

User question:
{query}

Give practical and concise career guidance.
Do not invent information that is not supported
by the provided career knowledge.
"""

    client = get_groq_client()
    if client:
        try:
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
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:
            pass

    top_context = "\n".join(context[:3])
    return (
        "Based on the available career knowledge, the most relevant guidance is: "
        f"\n\n{top_context}\n\n"
        "Use this information to build a hands-on learning plan and validate it against the specific role you're targeting."
    )