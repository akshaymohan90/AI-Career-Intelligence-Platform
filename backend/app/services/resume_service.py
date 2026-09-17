from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_parser import extract_text
from app.services.resume_analyzer import extract_basic_info


class ResumeService:

    def __init__(self):
        self.resume_repository = ResumeRepository()

    def upload_resume(
        self,
        db: Session,
        user_id: int,
        file: UploadFile
    ):

        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed")

        storage_dir = Path("storage/resumes")
        storage_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        stored_filename = (
            f"{uuid4()}_{file.filename}"
        )

        file_path = storage_dir / stored_filename

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        extracted_text = extract_text(str(file_path))

        resume = Resume(
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_type=file.content_type,
            status="Processed",
            extracted_text=extracted_text
        )

        return self.resume_repository.create(
            db,
            resume
        )



    def get_user_resumes(
        self,
        db: Session,
        user_id: int
    ):
        return self.resume_repository.get_by_user(
            db,
            user_id
        )



    def analyze_resume(
        self,
        db: Session,
        resume_id: int,
        user_id: int
    ):
        resume = self.resume_repository.get_by_id(
            db,
            resume_id,
            user_id
        )

        if not resume:
            raise ValueError("Resume not found")

        if not resume.extracted_text:
            raise ValueError("No text extracted from the resume")

        basic_info = extract_basic_info(
            resume.extracted_text
        )

        return basic_info

    