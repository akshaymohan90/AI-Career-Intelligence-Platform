from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import ResumeService
from app.schemas.resume import (ResumeResponse,ResumeAnalysisResponse)


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

resume_service = ResumeService()


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=201
)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return resume_service.upload_resume(
            db,
            current_user.id,
            file
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




@router.get(
    "/",
    response_model=list[ResumeResponse]
)
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.get_user_resumes(
        db,
        current_user.id
    )

@router.get(
    "/{resume_id}/analysis",
    response_model=ResumeAnalysisResponse
)
def analyze_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return resume_service.analyze_resume(
            db,
            resume_id,
            current_user.id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )