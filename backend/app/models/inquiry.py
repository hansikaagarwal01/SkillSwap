from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, Text, DateTime, Enum, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.listing import Listing

class MarketplaceInquiry(Base):
    __tablename__ = "marketplace_inquiry"
    __table_args__ = (
        CheckConstraint("buyer_roll_no <> seller_roll_no", name="chk_inquiry_buyer_seller_distinct"),
        Index("idx_inquiry_listing", "listing_id"),
        Index("idx_inquiry_seller_status", "seller_roll_no", "inquiry_status"),
        Index("idx_inquiry_buyer", "buyer_roll_no"),
    )

    inquiry_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("listing.listing_id", ondelete="CASCADE"),
        nullable=False
    )
    buyer_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT"),
        nullable=False
    )
    seller_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT"),
        nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    inquiry_status: Mapped[str] = mapped_column(
        Enum("PENDING", "RESPONDED", "CLOSED", name="inquiry_status_enum"),
        default="PENDING",
        nullable=False
    )
    email_delivery_status: Mapped[str] = mapped_column(
        Enum("SENT", "FAILED", "SKIPPED", name="email_delivery_status_enum"),
        default="SKIPPED",
        nullable=False
    )
    email_delivery_error: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    listing: Mapped["Listing"] = relationship("Listing")
    buyer: Mapped["Student"] = relationship("Student", foreign_keys=[buyer_roll_no])
    seller: Mapped["Student"] = relationship("Student", foreign_keys=[seller_roll_no])
