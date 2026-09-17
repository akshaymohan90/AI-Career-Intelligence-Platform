from app.services.job_matching import calculate_match


def test_job_matching():

    resume_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "FastAPI"
    ]

    job_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "FastAPI",
        "Docker"
    ]

    result = calculate_match(
        resume_skills,
        job_skills
    )

    assert result["match_score"] == 80.0

    assert set(result["matched_skills"]) == {
        "python",
        "sql",
        "machine learning",
        "fastapi"
    }

    assert result["missing_skills"] == [
        "docker"
    ]