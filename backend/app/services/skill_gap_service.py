from app.services.job_matching import calculate_match


def calculate_skill_gap(
    resume_skills: list[str],
    job_skills: list[str]
) -> dict:

    result = calculate_match(
        resume_skills,
        job_skills
    )

    return {
        "match_score": result["match_score"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "skill_gap_count": len(result["missing_skills"])
    }