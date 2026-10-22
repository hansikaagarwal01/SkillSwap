from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.skill import Skill
    from app.models.review import Review

class LearningSession(Base):
    __tablename__ = "learning_session"
    __table_args__ = (
        CheckConstraint("mentor_roll_no <> learner_roll_no", name="chk_session_distinct_participants"),
        CheckConstraint("credit_cost = 0", name="chk_session_free_credit_cost"),
        Index("idx_session_status_scheduled", "status", "scheduled_at"),
        Index("idx_session_mentor", "mentor_roll_no"),
        Index("idx_session_learner", "learner_roll_no"),
        Index("idx_session_skill", "skill_id"),
    )

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mentor_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False
    )
    learner_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(
        Enum("ONLINE", "OFFLINE", name="session_mode_enum"),
        default="ONLINE",
        nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    meeting_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("REQUESTED", "ACCEPTED", "REJECTED", "CANCELLED", "COMPLETED", name="session_status_enum"),
        default="REQUESTED",
        nullable=False
    )
    credit_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    mentor: Mapped["Student"] = relationship("Student", foreign_keys=[mentor_roll_no])
    learner: Mapped["Student"] = relationship("Student", foreign_keys=[learner_roll_no])
    skill: Mapped["Skill"] = relationship("Skill", back_populates="sessions")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="session", cascade="all, delete-orphan")
    reputation_reward: Mapped["ReputationHistory"] = relationship(
        "ReputationHistory",
        back_populates="session",
        uselist=False
    )


class ReputationHistory(Base):
    __tablename__ = "reputation_history"
    __table_args__ = (
        Index("idx_reputation_roll", "roll_no"),
    )

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_session.session_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        unique=True,
        nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="reputation_history")
    session: Mapped["LearningSession"] = relationship("LearningSession", back_populates="reputation_reward")
