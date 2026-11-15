from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, model_validator, field_validator

class ExperienceCreate(BaseModel):
    role_title: str
    organization: str
    exp_type: Literal["INTERNSHIP", "PROJECT", "HACKATHON", "ACHIEVEMENT", "OTHER"] = "PROJECT"
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None

    @field_validator("role_title", "organization")
    @classmethod
    def clean_text(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Field must be at least 2 characters long.")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be greater than or equal to start date.")
        return self


class ExperienceUpdate(BaseModel):
    role_title: Optional[str] = None
    organization: Optional[str] = None
    exp_type: Optional[Literal["INTERNSHIP", "PROJECT", "HACKATHON", "ACHIEVEMENT", "OTHER"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    @field_validator("role_title", "organization")
    @classmethod
    def clean_optional_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Field must be at least 2 characters long.")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be greater than or equal to start date.")
        return self


class ExperienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roll_no: str
    exp_no: int
    role_title: str
    organization: str
    exp_type: Literal["INTERNSHIP", "PROJECT", "HACKATHON", "ACHIEVEMENT", "OTHER"]
    start_date: date
    end_date: Optional[date]
    description: Optional[str]
    created_at: datetime
