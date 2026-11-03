from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

class InquiryCreate(BaseModel):
    message: str = Field(..., min_length=3, max_length=1000, description="Inquiry message to seller")

class InquiryStatusUpdate(BaseModel):
    status: Literal["PENDING", "RESPONDED", "CLOSED"] = Field(..., description="New inquiry status")

class InquiryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inquiry_id: int
    listing_id: int
    listing_title: str
    listing_price: Decimal
    buyer_roll_no: str
    buyer_name: str
    buyer_email: str
    seller_roll_no: str
    seller_name: str
    seller_email: str
    message: str
    inquiry_status: Literal["PENDING", "RESPONDED", "CLOSED"]
    email_delivery_status: Literal["SENT", "FAILED", "SKIPPED"]
    email_delivery_error: Optional[str] = None
    created_at: datetime

