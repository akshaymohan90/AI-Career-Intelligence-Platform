def generate_recommendations(
    missing_skills: list[str]
) -> list[dict]:

    return [
        {
            "skill": skill,
            "priority": "high"
        }
        for skill in missing_skills
    ]