from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, SmallInteger, DateTime, Enum, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.auth import AuthAccount, EmailVerificationToken
    from app.models.skill import StudentSkill
    from app.models.experience import Experience
    from app.models.session import ReputationHistory

class Student(Base):
    __tablename__ = "student"
    __table_args__ = (
        CheckConstraint(
            "roll_no REGEXP '^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$'",
            name="chk_student_roll_no_format"
        ),
        CheckConstraint(
            "program = SUBSTRING(roll_no, 5, LENGTH(program))",
            name="chk_student_program_matches_roll"
        ),
        CheckConstraint(
            "reputation_points >= 0",
            name="chk_student_reputation_positive"
        ),
        Index("idx_student_reputation", "reputation_points"),
        Index("idx_student_program_year", "program", "admission_year"),
    )

    roll_no: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    d_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.d_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    program: Mapped[str] = mapped_column(
        Enum("BTECH", "BBA", "BDES", name="student_program_enum"),
        nullable=False
    )
    admission_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reputation_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="students")
    auth_account: Mapped["AuthAccount"] = relationship("AuthAccount", back_populates="student", uselist=False, cascade="all, delete-orphan")
    skills: Mapped[list["StudentSkill"]] = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship("Experience", back_populates="student", cascade="all, delete-orphan")
    verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship("EmailVerificationToken", back_populates="student", cascade="all, delete-orphan")
    reputation_history: Mapped[list["ReputationHistory"]] = relationship("ReputationHistory", back_populates="student", cascade="all, delete-orphan")
