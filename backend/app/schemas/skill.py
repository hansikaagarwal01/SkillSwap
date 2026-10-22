from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class SkillCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Skill name must be at least 2 characters long.")
        return v

    @field_validator("category")
    @classmethod
    def clean_category(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category cannot be empty.")
        return v


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    name: str
    category: str
    description: Optional[str]
    created_at: datetime
