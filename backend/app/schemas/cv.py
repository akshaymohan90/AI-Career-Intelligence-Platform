from pydantic import BaseModel, ConfigDict, Field, model_validator


class _LenientModel(BaseModel):
    """LLM output may use null for absent facts or numbers for years; accept both."""

    model_config = ConfigDict(coerce_numbers_to_str=True)

    @model_validator(mode="before")
    @classmethod
    def _drop_nulls(cls, data):
        if isinstance(data, dict):
            return {key: value for key, value in data.items() if value is not None}
        return data


class CVExperience(_LenientModel):
    role: str | None = None
    company: str | None = None
    location: str | None = None
    start: str | None = None
    end: str | None = None
    bullets: list[str] = []


class CVEducation(_LenientModel):
    degree: str | None = None
    institution: str | None = None
    year: str | None = None
    details: str | None = None


class CVProject(_LenientModel):
    name: str = ""
    bullets: list[str] = []


class TailoredCV(_LenientModel):
    full_name: str = ""
    headline: str = ""
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = []
    summary: str = ""
    skills: list[str] = []
    experience: list[CVExperience] = []
    projects: list[CVProject] = []
    education: list[CVEducation] = []
    certifications: list[str] = []


class CVTailorRequest(BaseModel):
    resume_id: int
    job_title: str = Field(default="", max_length=150)
    company: str = Field(default="", max_length=150)
    job_description: str = Field(min_length=50, max_length=20000)


class ATSReport(BaseModel):
    keywords: list[str]
    matched_before: list[str]
    matched_after: list[str]
    missing: list[str]
    coverage_before: float
    coverage_after: float


class CVTailorResponse(BaseModel):
    cv: TailoredCV
    ats: ATSReport
    removed_skills: list[str]
    warnings: list[str]


class JobPostingOut(BaseModel):
    title: str
    company: str
    location: str | None
    description: str
    link: str | None
