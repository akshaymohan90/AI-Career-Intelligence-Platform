from datetime import datetime
from pydantic import BaseModel, ConfigDict




class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    original_filename: str
    file_path: str
    file_type: str
    status: str
    created_at: datetime


class ResumeAnalysisResponse(BaseModel):
    name: str | None
    skills: list[str]