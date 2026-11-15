from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, SmallInteger, DateTime, Enum, Boolean, CheckConstraint, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.skill import StudentSkill, StudentDesiredSkill
    from app.models.experience import Experience
    from app.models.department import Department

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
    program: Mapped[str] = mapped_column(
        Enum("BTECH", "BBA", "BDES", name="student_program_enum"),
        nullable=False
    )
    d_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("department.d_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True
    )
    admission_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reputation_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Consolidated Auth & Verification fields
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        Enum("STUDENT", "ADMIN", name="student_role_enum"),
        default="STUDENT",
        server_default="STUDENT",
        nullable=False
    )
    account_status: Mapped[str] = mapped_column(
        Enum("UNVERIFIED", "PENDING_APPROVAL", "ACTIVE", "SUSPENDED", name="account_status_enum"),
        default="UNVERIFIED",
        nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    verification_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    verification_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    dept_rel: Mapped[Optional["Department"]] = relationship("Department")
    skills: Mapped[list["StudentSkill"]] = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    desired_skills: Mapped[list["StudentDesiredSkill"]] = relationship("StudentDesiredSkill", back_populates="student", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship("Experience", back_populates="student", cascade="all, delete-orphan")

    # Compatibility Helpers
    @property
    def auth_account(self):
        """Allow backwards-compatible access to auth properties via current_user.auth_account"""
        return self

    @property
    def department(self) -> str:
        if self.dept_rel:
            return self.dept_rel.name
        prog_map = {
            "BTECH": "Computer Science and Engineering",
            "BBA": "Institute of Management",
            "BDES": "Institute of Design",
        }
        return prog_map.get(self.program, "Computer Science and Engineering")

    @property
    def resolved_d_id(self) -> int:
        if self.d_id is not None:
            return self.d_id
        dept_ids = {
            "BTECH": 1,
            "BBA": 4,
            "BDES": 5
        }
        return dept_ids.get(self.program, 1)

    @property
    def department_name(self) -> str:
        return self.department
