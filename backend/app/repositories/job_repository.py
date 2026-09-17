from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job

class JobRepository:
    
    def create(
        self,
        db: Session,
        job: Job
    ) -> Job:
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get_all(
        self,
        db: Session
    ) -> list[Job]:
        return db.execute(select(Job)).scalars().all()

    def get_by_id(
        self,
        db: Session,
        job_id: int
    ) -> Job | None:
        return db.get(Job, job_id)