from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, Text, DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.session import LearningSession

class Skill(Base):
    __tablename__ = "skill"
    __table_args__ = (
        Index("idx_skill_category", "category"),
    )

    skill_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    students: Mapped[list["StudentSkill"]] = relationship("StudentSkill", back_populates="skill")
    sessions: Mapped[list["LearningSession"]] = relationship("LearningSession", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skill"
    __table_args__ = (
        Index("idx_student_skill_teach", "can_teach", "skill_id"),
    )

    roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    )
    proficiency_level: Mapped[str] = mapped_column(
        Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT", name="proficiency_level_enum"),
        default="BEGINNER",
        nullable=False
    )
    can_teach: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="students")
