from datetime import datetime

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(100), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(200), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="uploaded")
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    user = relationship("User", backref="resumes")

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)