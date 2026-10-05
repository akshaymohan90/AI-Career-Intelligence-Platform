from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.schemas.cv import CVTailorRequest, CVTailorResponse, JobPostingOut, TailoredCV
from app.services.cv_render import render_docx, render_pdf, safe_filename
from app.services.cv_tailor import CVTailorBusyError, CVTailorError, tailor_cv
from app.services.serpapi_client import SerpApiClient, SerpApiError

router = APIRouter(prefix="/cv", tags=["CV Builder"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.post("/tailor", response_model=CVTailorResponse)
def tailor(
    data: CVTailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = ResumeRepository().get_by_id(db, data.resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.extracted_text:
        raise HTTPException(status_code=422, detail="Resume has no extracted text yet")

    try:
        return tailor_cv(resume.extracted_text, data.job_title, data.company, data.job_description)
    except CVTailorBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except CVTailorError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


def _download(content: bytes, media_type: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/render/pdf")
def download_pdf(cv: TailoredCV, current_user: User = Depends(get_current_user)):
    return _download(render_pdf(cv), "application/pdf", safe_filename(cv, "pdf"))


@router.post("/render/docx")
def download_docx(cv: TailoredCV, current_user: User = Depends(get_current_user)):
    return _download(render_docx(cv), DOCX_MIME, safe_filename(cv, "docx"))


@router.get("/job-search", response_model=list[JobPostingOut])
def job_search(
    q: str = Query(min_length=2, max_length=120),
    location: str = Query(default="India", max_length=120),
    current_user: User = Depends(get_current_user),
):
    try:
        data = SerpApiClient().search("google_jobs", q=q, location=location)
    except SerpApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    postings = []
    for job in data.get("jobs_results", []):
        options = job.get("apply_options") or []
        postings.append({
            "title": job.get("title", "Untitled role"),
            "company": job.get("company_name", "Unknown company"),
            "location": job.get("location"),
            "description": job.get("description", ""),
            "link": (options[0].get("link") if options else None) or job.get("share_link"),
        })
    return postings
