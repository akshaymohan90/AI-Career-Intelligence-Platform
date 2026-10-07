from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import ALLOWED_ORIGINS
from app.database.base import base
from app.database.database import engine
from app.models.user import User
from app.services.career_knowledge import load_career_knowledge


def create_db_tables() -> None:
    base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SkillRadar",
    version="1.0.0",
    description="Ranks skills by jobs unlocked per week of learning using live SerpApi data, and builds ATS-ready CVs."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_tables()
load_career_knowledge()
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "SkillRadar API is running!"
    }