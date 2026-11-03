import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    hash_token,
    generate_verification_token
)
from app.models.student import Student
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserMeResponse

logger = logging.getLogger("skillswap.auth")

class AuthService:
    @staticmethod
    def derive_program_and_year(roll_no: str) -> tuple[str, int]:
        year = int(roll_no[:4])
        if "BTECH" in roll_no:
            program = "BTECH"
        elif "BBA" in roll_no:
            program = "BBA"
        elif "BDES" in roll_no:
            program = "BDES"
        else:
            raise ValueError("Unsupported program in roll number.")
        return program, year

    @classmethod
    def register(cls, db: Session, req: RegisterRequest) -> dict[str, str]:
        # Check if roll_no already exists
        existing_roll = db.query(Student).filter(Student.roll_no == req.roll_no).first()
        if existing_roll:
            if existing_roll.password_hash is None:
                # Unclaimed survey profile: allow student to securely claim and activate their account
                if existing_roll.email.lower() != req.email.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "EMAIL_MISMATCH", "message": f"Email {req.email} does not match the college record on file for {req.roll_no}."}
                    )
                raw_token = generate_verification_token()
                token_hashed = hash_token(raw_token)
                expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

                if req.name and req.name.strip():
                    existing_roll.name = req.name.strip()
                if req.phone:
                    existing_roll.phone = req.phone.strip()
                existing_roll.password_hash = get_password_hash(req.password)
                existing_roll.account_status = "UNVERIFIED"
                existing_roll.email_verified = False
                existing_roll.token_version = 1
                existing_roll.verification_token_hash = token_hashed
                existing_roll.verification_token_expires_at = expires_at
                db.commit()

                if settings.APP_ENV == "development":
                    logger.info(
                        "\n============================== [DEV-ONLY VERIFICATION LINK] ==============================\n"
                        f"Student: {req.roll_no} ({req.email})\n"
                        f"Token: {raw_token}\n"
                        f"Verification URL: {settings.FRONTEND_ORIGIN}/verify-email?token={raw_token}\n"
                        "=========================================================================================\n"
                    )

                return {
                    "message": "Survey profile claimed successfully. Please verify your email to activate your account.",
                    "roll_no": req.roll_no
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "ROLL_NO_EXISTS", "message": "An account with this roll number already exists."}
                )

        # Check if email already exists
        existing_email = db.query(Student).filter(Student.email == req.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "EMAIL_EXISTS", "message": "An account with this email address already exists."}
            )

        program, admission_year = cls.derive_program_and_year(req.roll_no)

        # Generate Email Verification Token
        raw_token = generate_verification_token()
        token_hashed = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        try:
            # Create consolidated Student record
            new_student = Student(
                roll_no=req.roll_no,
                name=req.name,
                email=req.email,
                phone=req.phone,
                program=program,
                admission_year=admission_year,
                reputation_points=0,
                password_hash=get_password_hash(req.password),
                account_status="UNVERIFIED",
                email_verified=False,
                token_version=1,
                verification_token_hash=token_hashed,
                verification_token_expires_at=expires_at
            )
            db.add(new_student)
            db.commit()

            # Handle Email Delivery / Dev Logging
            if settings.APP_ENV == "development":
                logger.info(
                    "\n============================== [DEV-ONLY VERIFICATION LINK] ==============================\n"
                    f"Student: {req.roll_no} ({req.email})\n"
                    f"Token: {raw_token}\n"
                    f"Verification URL: {settings.FRONTEND_ORIGIN}/verify-email?token={raw_token}\n"
                    "=========================================================================================\n"
                )

            return {
                "message": "Registration successful. Please verify your email address to activate your account.",
                "roll_no": req.roll_no
            }

        except Exception as e:
            db.rollback()
            logger.error("Failed to register student: %s", str(e))
            raise

    @classmethod
    def verify_email(cls, db: Session, raw_token: str) -> dict[str, str]:
        token_hashed = hash_token(raw_token.strip())
        student = db.query(Student).filter(Student.verification_token_hash == token_hashed).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TOKEN", "message": "Verification token is invalid."}
            )

        # Check expiration
        now = datetime.now(timezone.utc)
        record_expiry = student.verification_token_expires_at
        if record_expiry is not None:
            if record_expiry.tzinfo is None:
                record_expiry = record_expiry.replace(tzinfo=timezone.utc)
            if record_expiry < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "TOKEN_EXPIRED", "message": "Verification token has expired. Please request a new one."}
                )

        # Mark verified & invalidate used token
        student.verification_token_hash = None
        student.verification_token_expires_at = None
        student.email_verified = True

        if settings.REQUIRE_ADMIN_APPROVAL:
            student.account_status = "PENDING_APPROVAL"
        else:
            student.account_status = "ACTIVE"

        db.commit()

        status_msg = (
            "Account email verified. Pending administrator approval."
            if settings.REQUIRE_ADMIN_APPROVAL
            else "Email verified successfully. Your account is now active."
        )
        return {"message": status_msg, "roll_no": student.roll_no}

    @classmethod
    def resend_verification(cls, db: Session, email: str) -> dict[str, str]:
        student = db.query(Student).filter(Student.email == email).first()
        generic_msg = "If an unverified account exists for this email, a new verification link has been sent."

        if not student or student.email_verified:
            return {"message": generic_msg}

        raw_token = generate_verification_token()
        token_hashed = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        student.verification_token_hash = token_hashed
        student.verification_token_expires_at = expires_at
        db.commit()

        if settings.APP_ENV == "development":
            logger.info(
                "\n============================== [DEV-ONLY VERIFICATION RESEND] ==============================\n"
                f"Student: {student.roll_no} ({student.email})\n"
                f"Token: {raw_token}\n"
                f"Verification URL: {settings.FRONTEND_ORIGIN}/verify-email?token={raw_token}\n"
                "=========================================================================================\n"
            )

        return {"message": generic_msg}

    @classmethod
    def login(cls, db: Session, req: LoginRequest) -> TokenResponse:
        student = db.query(Student).filter(Student.roll_no == req.roll_no).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid roll number or password."}
            )

        if not student.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ACCOUNT_UNCLAIMED", "message": "Your profile is registered from the survey but has not been claimed. Please register to claim your profile and set a password."}
            )

        if not verify_password(req.password, student.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid roll number or password."}
            )

        if not student.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "EMAIL_UNVERIFIED", "message": "Please verify your email before logging in."}
            )

        if student.account_status == "PENDING_APPROVAL":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "PENDING_APPROVAL", "message": "Your account is pending administrator approval."}
            )

        if student.account_status == "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_SUSPENDED", "message": "Your account has been suspended by administration."}
            )

        if student.account_status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "Account is not active."}
            )

        # Update last login
        student.last_login_at = datetime.now(timezone.utc)
        db.commit()

        access_token = create_access_token(
            subject=student.roll_no,
            role=student.role,
            token_version=student.token_version
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            roll_no=student.roll_no,
            name=student.name,
            role=student.role,
            account_status=student.account_status
        )

    @classmethod
    def get_me(cls, student: Student) -> UserMeResponse:
        return UserMeResponse(
            roll_no=student.roll_no,
            name=student.name,
            email=student.email,
            phone=student.phone,
            department=student.department,
            department_name=student.department,
            d_id=student.d_id,
            program=student.program,
            admission_year=student.admission_year,
            reputation_points=student.reputation_points,
            role=student.role,
            account_status=student.account_status,
            email_verified=student.email_verified,
            created_at=student.created_at
        )
