import re
from app.services.skill_normalizer import normalize_skills


def extract_basic_info(text: str) -> dict:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    skills = normalize_skills(extract_skills(text))

    return {
        "name": lines[0] if lines else None,
        "skills": skills,
    }


def extract_skills(text: str) -> list[str]:

    skill_list = [
        "Python",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "FastAPI",
        "Django",
        "Java",
        "JavaScript",
        "React",
        "Next.js",
        "PostgreSQL",
        "MongoDB",
        "Docker",
        "Kubernetes",
        "AWS",
        "Git",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch"
    ]

    text_lower = text.lower()

    found_skills = []

    for skill in skill_list:
        if re.search(
            rf"\b{re.escape(skill.lower())}\b",
            text_lower
        ):
            found_skills.append(skill)

    return found_skills