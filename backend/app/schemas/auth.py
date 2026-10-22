import re
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from email_validator import validate_email, EmailNotValidError
from app.core.security import validate_password_strength

ROLL_NO_REGEX = re.compile(r"^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$")

class RegisterRequest(BaseModel):
    roll_no: str
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    d_id: int

    @field_validator("roll_no")
    @classmethod
    def validate_roll_no(cls, v: str) -> str:
        v = v.strip().upper()
        if not ROLL_NO_REGEX.match(v):
            raise ValueError(
                "Invalid Roll Number format. Must match ^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$ (e.g., 2025BTECH027)"
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_jklu_email(cls, v: str) -> str:
        v = v.strip().lower()
        try:
            valid = validate_email(v, check_deliverability=False)
            normalized = valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email format: {str(e)}")

        parts = normalized.split("@")
        if len(parts) != 2 or parts[1] != "jklu.edu.in":
            raise ValueError("Only official JKLU email addresses (@jklu.edu.in) are permitted.")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        ok, msg = validate_password_strength(v)
        if not ok:
            raise ValueError(msg)
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        v = v.strip()
        if not re.match(r"^[0-9+\-\s]{7,15}$", v):
            raise ValueError("Phone number must contain between 7 and 15 digits/valid characters.")
        return v


class LoginRequest(BaseModel):
    roll_no: str
    password: str

    @field_validator("roll_no")
    @classmethod
    def normalize_roll(cls, v: str) -> str:
        return v.strip().upper()


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    roll_no: str
    name: str
    role: str
    account_status: str


class UserMeResponse(BaseModel):
    roll_no: str
    name: str
    email: str
    phone: Optional[str]
    d_id: int
    department_name: Optional[str]
    program: Literal["BTECH", "BBA", "BDES"]
    admission_year: int
    reputation_points: int
    role: Literal["STUDENT", "ADMIN"]
    account_status: Literal["UNVERIFIED", "PENDING_APPROVAL", "ACTIVE", "SUSPENDED"]
    email_verified: bool
    created_at: datetime
