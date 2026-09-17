from app.services.career_knowledge import load_career_knowledge
from app.services.rag_service import generate_rag_answer


load_career_knowledge()

answer = generate_rag_answer(
    "What should I learn to improve my Docker skills?"
)

print(answer)