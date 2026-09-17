def calculate_match(
    resume_skills: list[str],
    job_skills: list[str]
) -> dict:

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    job_set = {
        skill.strip().lower()
        for skill in job_skills
    }

    matched = resume_set.intersection(job_set)
    missing = job_set - resume_set

    score = (
        len(matched) / len(job_set) * 100
        if job_set
        else 0
    )

    return {
        "match_score": round(score, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }