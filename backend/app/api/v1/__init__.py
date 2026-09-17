from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(jobs_router)
router.include_router(resumes_router)