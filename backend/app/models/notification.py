from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.inquiry import MarketplaceInquiry

class Notification(Base):
    __tablename__ = "notification"
    __table_args__ = (
        Index("idx_notification_recipient_read", "recipient_roll_no", "is_read"),
    )

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="CASCADE"),
        nullable=False
    )
    inquiry_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("marketplace_inquiry.inquiry_id", ondelete="SET NULL"),
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    recipient: Mapped["Student"] = relationship("Student", foreign_keys=[recipient_roll_no])
    inquiry: Mapped[Optional["MarketplaceInquiry"]] = relationship("MarketplaceInquiry", foreign_keys=[inquiry_id])
