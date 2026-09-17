from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str
    company: str
    location: str | None = None
    experience_required: str | None = None
    required_skills: str | None = None


class JobResponse(JobCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class JobMatchResponse(BaseModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]


class CareerAnalysisResponse(BaseModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    skill_gap_count: int
    recommendations: list[dict]


class CareerAdviceResponse(BaseModel):
    advice: str

class CareerAssistantResponse(BaseModel):
    answer: str