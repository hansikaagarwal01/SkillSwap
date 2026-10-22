from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, SmallInteger, Text, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.session import LearningSession
    from app.models.student import Student

class Review(Base):
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="chk_review_rating_range"),
        CheckConstraint("roll_no <> reviewee_roll_no", name="chk_review_distinct_parties"),
        Index("idx_review_roll", "roll_no"),
        Index("idx_review_reviewee", "reviewee_roll_no"),
    )

    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_session.session_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        primary_key=True
    )
    roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        primary_key=True
    )
    reviewee_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    session: Mapped["LearningSession"] = relationship("LearningSession", back_populates="reviews")
    reviewer: Mapped["Student"] = relationship("Student", foreign_keys=[roll_no])
    reviewee: Mapped["Student"] = relationship("Student", foreign_keys=[reviewee_roll_no])
