from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ListingCreate(BaseModel):
    title: str
    description: str
    price: Decimal = Field(..., ge=0)
    category: str
    item_condition: Literal["NEW", "LIKE_NEW", "GOOD", "FAIR"] = "GOOD"

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters.")
        return v


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = None
    item_condition: Optional[Literal["NEW", "LIKE_NEW", "GOOD", "FAIR"]] = None
    status: Optional[Literal["AVAILABLE", "IN_PROGRESS", "SOLD", "REMOVED"]] = None


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    listing_id: int
    seller_roll_no: str
    seller_name: Optional[str] = None
    buyer_roll_no: Optional[str] = None
    buyer_name: Optional[str] = None
    title: str
    description: str
    status: Literal["AVAILABLE", "IN_PROGRESS", "SOLD", "REMOVED", "PENDING_REVIEW"]
    price: Decimal
    original_price_text: Optional[str] = None
    category: str
    item_condition: Literal["NEW", "LIKE_NEW", "GOOD", "FAIR"]
    posted_date: datetime
    sold_at: Optional[datetime] = None
