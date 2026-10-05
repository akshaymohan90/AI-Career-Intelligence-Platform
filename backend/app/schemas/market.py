from pydantic import BaseModel, Field


class MarketScanRequest(BaseModel):
    role: str = Field(min_length=2, max_length=120, examples=["backend engineer"])
    location: str = Field(min_length=2, max_length=120, examples=["Bangalore, Karnataka, India"])
    resume_id: int


class PostingEvidence(BaseModel):
    title: str
    company: str
    location: str | None
    link: str | None
    gaps_in_posting: int


class SkillRecommendation(BaseModel):
    skill: str
    jobs_unlocked: float
    estimated_weeks: int
    jobs_per_week: float
    trend_direction: str
    trend_momentum: float | None
    score: float
    evidence: list[PostingEvidence]


class AgentStep(BaseModel):
    step: str
    detail: str
    ms: int


class MarketScanResponse(BaseModel):
    role: str
    location: str
    postings_scanned: int
    postings_analyzed: int
    your_skills: list[str]
    already_qualified: int
    near_matches: int
    recommendations: list[SkillRecommendation]
    agent_trace: list[AgentStep]
    serpapi_live_calls: int
    serpapi_cache_hits: int
