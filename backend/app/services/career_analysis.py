from app.services.skill_gap_service import calculate_skill_gap
from app.services.recommendation_service import generate_recommendations


def analyze_career_fit(
    resume_skills: list[str],
    job_skills: list[str]
) -> dict:

    gap = calculate_skill_gap(
        resume_skills,
        job_skills
    )

    recommendations = generate_recommendations(
        gap["missing_skills"]
    )

    return {
        **gap,
        "recommendations": recommendations
    }