from datetime import datetime, date
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Date, DateTime, Enum, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student

class Experience(Base):
    __tablename__ = "experience"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="chk_experience_dates"),
    )

    roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    )
    exp_no: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    organization: Mapped[str] = mapped_column(String(150), nullable=False)
    exp_type: Mapped[str] = mapped_column(
        Enum("INTERNSHIP", "PROJECT", "HACKATHON", "ACHIEVEMENT", "OTHER", name="exp_type_enum"),
        default="PROJECT",
        nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="experiences")
