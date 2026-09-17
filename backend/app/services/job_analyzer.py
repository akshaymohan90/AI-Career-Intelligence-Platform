from app.services.skill_normalizer import normalize_skills
from app.services.resume_analyzer import extract_skills


def extract_job_skills(description: str) -> list[str]:
    skills = extract_skills(description)

    return normalize_skills(skills)