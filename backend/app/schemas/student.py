from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator
import re

class StudentSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"] = "BEGINNER"
    can_teach: bool = False


class StudentSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roll_no: str
    skill_id: int
    skill_name: Optional[str] = None
    category: Optional[str] = None
    proficiency_level: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
    can_teach: bool
    created_at: datetime


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    d_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters.")
        return v

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r"^[0-9+\-\s]{7,15}$", v):
                raise ValueError("Phone number must contain between 7 and 15 digits/valid characters.")
        return v


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roll_no: str
    name: str
    email: str
    phone: Optional[str]
    d_id: int
    department_name: Optional[str] = None
    program: Literal["BTECH", "BBA", "BDES"]
    admission_year: int
    reputation_points: int
    created_at: datetime
    skills: list[StudentSkillResponse] = []


class MentorResponse(BaseModel):
    roll_no: str
    name: str
    email: str
    program: Literal["BTECH", "BBA", "BDES"]
    admission_year: int
    reputation_points: int
    department_name: Optional[str] = None
    skill_id: int
    skill_name: str
    proficiency_level: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
    avg_rating: Optional[float] = None
    total_reviews: int = 0
    completed_sessions: int = 0
