from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate
from app.services.job_analyzer import extract_job_skills
from app.services.job_matching import calculate_match
from app.services.resume_analyzer import extract_skills
from app.repositories.resume_repository import ResumeRepository


class JobService:

    def __init__(self):
        self.repository = JobRepository()
        self.resume_repository = ResumeRepository()

    def create_job(
        self,
        db: Session,
        data: JobCreate
    ) -> Job:

        job = Job(
            title=data.title,
            company=data.company,
            description=data.description,
            location=data.location,
            experience_required=data.experience_required,
            required_skills=data.required_skills or ", ".join(
                extract_job_skills(data.description)
            )
        )

        return self.repository.create(
            db,
            job
        )

    def get_job(
        self,
        db: Session,
        job_id: int
    ) -> Job | None:

        return self.repository.get_by_id(
            db,
            job_id
        )

    def get_jobs(
        self,
        db: Session
    ) -> list[Job]:

        return self.repository.get_all(db)


    def get_job_skills(
        self,
        db: Session,
        job_id: int
    ) -> list[str]:

        job = self.repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise ValueError("Job not found")

        if not job.required_skills:
            return []

        return [
            skill.strip()
            for skill in job.required_skills.split(",")
            if skill.strip()
        ]


    def match_resume(
        self,
        db: Session,
        job_id: int,
        resume_id: int,
        user_id: int
    ):
        job = self.repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise ValueError("Job not found")

        resume = self.resume_repository.get_by_id(
            db,
            resume_id,
            user_id
        )

        if not resume:
            raise ValueError("Resume not found")

        resume_skills = extract_skills(resume.extracted_text or "")

        job_skills = self.get_job_skills(
            db,
            job_id
        )

        return calculate_match(
            resume_skills,
            job_skills
        )