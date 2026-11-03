from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    recipient_roll_no: str
    inquiry_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime

class UnreadCountResponse(BaseModel):
    unread_count: int

