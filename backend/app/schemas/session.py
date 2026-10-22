from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class SessionCreate(BaseModel):
    mentor_roll_no: str
    skill_id: int
    topic: str
    mode: Literal["ONLINE", "OFFLINE"] = "ONLINE"
    scheduled_at: datetime
    meeting_link: Optional[str] = None

    @field_validator("topic")
    @classmethod
    def clean_topic(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Topic must be at least 3 characters.")
        return v


class SessionReschedule(BaseModel):
    scheduled_at: Optional[datetime] = None
    new_scheduled_at: Optional[datetime] = None

    @model_validator(mode="after")
    def resolve_time(self):
        if not self.scheduled_at and not self.new_scheduled_at:
            raise ValueError("Scheduled time must be provided.")
        if not self.scheduled_at:
            self.scheduled_at = self.new_scheduled_at
        return self


class SessionStatusUpdate(BaseModel):
    status: Literal["ACCEPTED", "REJECTED", "CANCELLED", "COMPLETED"]


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    mentor_roll_no: str
    mentor_name: Optional[str] = None
    learner_roll_no: str
    learner_name: Optional[str] = None
    skill_id: int
    skill_name: Optional[str] = None
    topic: str
    mode: Literal["ONLINE", "OFFLINE"]
    scheduled_at: datetime
    meeting_link: Optional[str] = None
    status: Literal["REQUESTED", "ACCEPTED", "REJECTED", "CANCELLED", "COMPLETED"]
    credit_cost: int = 0
    created_at: datetime
    updated_at: datetime
    has_review: bool = False


class ReviewCreate(BaseModel):
    session_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    roll_no: str
    reviewer_name: Optional[str] = None
    reviewee_roll_no: str
    reviewee_name: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime
