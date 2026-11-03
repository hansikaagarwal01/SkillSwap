from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, Numeric, Text, DateTime, Enum, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student

class Listing(Base):
    __tablename__ = "listing"
    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_listing_price_positive"),
        CheckConstraint("buyer_roll_no IS NULL OR seller_roll_no <> buyer_roll_no", name="chk_listing_seller_buyer_distinct"),
        CheckConstraint(
            "(status = 'SOLD' AND buyer_roll_no IS NOT NULL AND sold_at IS NOT NULL) OR (status <> 'SOLD')",
            name="chk_listing_sold_consistency"
        ),
        Index("idx_listing_seller", "seller_roll_no"),
        Index("idx_listing_buyer", "buyer_roll_no"),
        Index("idx_listing_status_category", "status", "category"),
    )

    listing_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_roll_no: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False
    )
    buyer_roll_no: Mapped[str | None] = mapped_column(
        String(12),
        ForeignKey("student.roll_no", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("AVAILABLE", "IN_PROGRESS", "SOLD", "REMOVED", "PENDING_REVIEW", name="listing_status_enum"),
        default="AVAILABLE",
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    original_price_text: Mapped[str | None] = mapped_column(String(150), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    item_condition: Mapped[str] = mapped_column(
        Enum("NEW", "LIKE_NEW", "GOOD", "FAIR", name="item_condition_enum"),
        default="GOOD",
        nullable=False
    )
    posted_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    seller: Mapped["Student"] = relationship("Student", foreign_keys=[seller_roll_no])
    buyer: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[buyer_roll_no])
