from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Enum, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class SurveyImportAudit(Base):
    __tablename__ = "survey_import_audit"
    __table_args__ = (
        Index("idx_audit_roll", "normalized_roll_no"),
        Index("idx_audit_status", "import_status"),
    )

    submission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    student_name: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_roll_no: Mapped[str] = mapped_column(String(50), nullable=False)
    normalized_roll_no: Mapped[str | None] = mapped_column(String(12), nullable=True)
    raw_email: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_current_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_desired_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_sell_flag: Mapped[str | None] = mapped_column(String(10), nullable=True)
    raw_item: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_price: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    import_status: Mapped[str] = mapped_column(
        Enum("IMPORTED", "MERGED_DUPLICATE", "REQUIRES_REVIEW", "REJECTED", name="import_status_enum"),
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

