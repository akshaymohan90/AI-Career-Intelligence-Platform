from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService
from app.schemas.job import JobMatchResponse
from app.models.user import User
from app.services.career_analysis import analyze_career_fit
from app.schemas.job import CareerAnalysisResponse
from app.services.resume_analyzer import extract_skills
from app.services.ai_service import generate_career_advice
from app.schemas.job import CareerAdviceResponse
from app.services.career_assistant import (
    generate_career_assistant_response
)

from app.schemas.job import CareerAssistantResponse


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

job_service = JobService()


@router.post(
    "/",
    response_model=JobResponse,
    status_code=201
)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db)
):
    return job_service.create_job(
        db,
        data
    )


@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db)
):
    return job_service.get_jobs(db)




@router.get(
    "/{job_id}/skills",
    response_model=list[str]
)
def get_job_skills(
    job_id: int,
    db: Session = Depends(get_db)
):
    try:
        return job_service.get_job_skills(
            db,
            job_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = job_service.get_job(
        db,
        job_id
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@router.post(
    "/{job_id}/match/{resume_id}",
    response_model=JobMatchResponse
)
def match_job(
    job_id: int,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return job_service.match_resume(
            db,
            job_id,
            resume_id,
            current_user.id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.post(
    "/{job_id}/career-analysis/{resume_id}",
    response_model=CareerAnalysisResponse
)
def career_analysis(
    job_id: int,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        job = job_service.repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise ValueError("Job not found")

        resume = job_service.resume_repository.get_by_id(
            db,
            resume_id,
            current_user.id
        )

        if not resume:
            raise ValueError("Resume not found")

        resume_skills = extract_skills(resume.extracted_text or "")

        job_skills = job_service.get_job_skills(
            db,
            job_id
        )

        return analyze_career_fit(
            resume_skills,
            job_skills
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post(
    "/{job_id}/ai-advice/{resume_id}",
    response_model=CareerAdviceResponse
)
def ai_career_advice(
    job_id: int,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        job = job_service.repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise ValueError("Job not found")

        resume = job_service.resume_repository.get_by_id(
            db,
            resume_id,
            current_user.id
        )

        if not resume:
            raise ValueError("Resume not found")

        resume_skills = extract_skills(resume.extracted_text or "")

        job_skills = job_service.get_job_skills(
            db,
            job_id
        )

        advice = generate_career_advice(
            resume_skills,
            job_skills
        )

        return {
            "advice": advice
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=502,
            detail=str(e)
        )
@router.post(
    "/{job_id}/assistant/{resume_id}",
    response_model=CareerAssistantResponse
)
def career_assistant(
    job_id: int,
    resume_id: int,
    question: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        job = job_service.repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise ValueError("Job not found")

        resume = job_service.resume_repository.get_by_id(
            db,
            resume_id,
            current_user.id
        )

        if not resume:
            raise ValueError("Resume not found")

        resume_skills = extract_skills(resume.extracted_text or "")

        job_skills = job_service.get_job_skills(
            db,
            job_id
        )

        answer = generate_career_assistant_response(
            question,
            resume_skills,
            job_skills
        )

        return {
            "answer": answer
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )