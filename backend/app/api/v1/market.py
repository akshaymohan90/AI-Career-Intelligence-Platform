from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.schemas.market import MarketScanRequest, MarketScanResponse
from app.services.market_intelligence import run_market_scan
from app.services.serpapi_client import SerpApiClient, SerpApiError

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.post("/scan", response_model=MarketScanResponse)
def market_scan(
    data: MarketScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = ResumeRepository().get_by_id(db, data.resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.extracted_text:
        raise HTTPException(status_code=422, detail="Resume has no extracted text yet")

    try:
        return run_market_scan(
            SerpApiClient(),
            role=data.role,
            location=data.location,
            resume_text=resume.extracted_text,
        )
    except SerpApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
