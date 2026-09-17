SKILL_ALIASES = {
    "python 3": "Python",
    "python programming": "Python",
    "python": "Python",

    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "machine learning": "Machine Learning",

    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "js": "JavaScript",
    "javascript": "JavaScript",

    "reactjs": "React",
    "react.js": "React",
    "react": "React",
}


def normalize_skills(skills: list[str]) -> list[str]:

    normalized = []

    for skill in skills:
        key = skill.strip().lower()

        standard_skill = SKILL_ALIASES.get(
            key,
            skill.strip()
        )

        if standard_skill not in normalized:
            normalized.append(standard_skill)

    return normalized