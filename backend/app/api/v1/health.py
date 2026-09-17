from fastapi import APIRouter
router = APIRouter()
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "ai career intelligence platform",
        "version": "1.0.0"
    }