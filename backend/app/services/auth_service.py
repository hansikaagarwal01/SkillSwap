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
from app.models.auth import AuthAccount, EmailVerificationToken
from app.models.department import Department
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "ROLL_NO_EXISTS", "message": "An account with this roll number already exists."}
            )

        # Check if email already exists (generic error message prevents enumeration)
        existing_email = db.query(Student).filter(Student.email == req.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "EMAIL_EXISTS", "message": "An account with this email address already exists."}
            )

        # Verify department exists
        dept = db.query(Department).filter(Department.d_id == req.d_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DEPARTMENT_NOT_FOUND", "message": "Selected department does not exist."}
            )

        program, admission_year = cls.derive_program_and_year(req.roll_no)

        try:
            # Create Student
            new_student = Student(
                roll_no=req.roll_no,
                name=req.name,
                email=req.email,
                phone=req.phone,
                d_id=req.d_id,
                program=program,
                admission_year=admission_year,
                reputation_points=0
            )
            db.add(new_student)

            # Create AuthAccount
            auth_acc = AuthAccount(
                roll_no=req.roll_no,
                password_hash=get_password_hash(req.password),
                role="STUDENT",
                account_status="UNVERIFIED",
                email_verified=False,
                token_version=1
            )
            db.add(auth_acc)

            # Generate Email Verification Token
            raw_token = generate_verification_token()
            token_hashed = hash_token(raw_token)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

            v_token = EmailVerificationToken(
                roll_no=req.roll_no,
                token_hash=token_hashed,
                expires_at=expires_at
            )
            db.add(v_token)

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
        record = db.query(EmailVerificationToken).filter(EmailVerificationToken.token_hash == token_hashed).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TOKEN", "message": "Verification token is invalid."}
            )

        if record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "TOKEN_ALREADY_USED", "message": "Verification token has already been used."}
            )

        # Check expiration
        now = datetime.now(timezone.utc)
        record_expiry = record.expires_at
        if record_expiry.tzinfo is None:
            record_expiry = record_expiry.replace(tzinfo=timezone.utc)

        if record_expiry < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "TOKEN_EXPIRED", "message": "Verification token has expired. Please request a new one."}
            )

        # Mark token used
        record.used_at = now

        # Update auth account
        auth_acc = db.query(AuthAccount).filter(AuthAccount.roll_no == record.roll_no).first()
        if not auth_acc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ACCOUNT_NOT_FOUND", "message": "Associated account not found."}
            )

        auth_acc.email_verified = True
        if settings.REQUIRE_ADMIN_APPROVAL:
            auth_acc.account_status = "PENDING_APPROVAL"
        else:
            auth_acc.account_status = "ACTIVE"

        db.commit()

        status_msg = (
            "Account email verified. Pending administrator approval."
            if settings.REQUIRE_ADMIN_APPROVAL
            else "Email verified successfully. Your account is now active."
        )
        return {"message": status_msg, "roll_no": record.roll_no}

    @classmethod
    def resend_verification(cls, db: Session, email: str) -> dict[str, str]:
        student = db.query(Student).filter(Student.email == email).first()
        # Always return generic success to prevent email enumeration
        generic_msg = "If an unverified account exists for this email, a new verification link has been sent."

        if not student or not student.auth_account or student.auth_account.email_verified:
            return {"message": generic_msg}

        raw_token = generate_verification_token()
        token_hashed = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        v_token = EmailVerificationToken(
            roll_no=student.roll_no,
            token_hash=token_hashed,
            expires_at=expires_at
        )
        db.add(v_token)
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
        if not student or not student.auth_account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid roll number or password."}
            )

        auth_acc = student.auth_account
        if not verify_password(req.password, auth_acc.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid roll number or password."}
            )

        if not auth_acc.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "EMAIL_UNVERIFIED", "message": "Please verify your email before logging in."}
            )

        if auth_acc.account_status == "PENDING_APPROVAL":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "PENDING_APPROVAL", "message": "Your account is pending administrator approval."}
            )

        if auth_acc.account_status == "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_SUSPENDED", "message": "Your account has been suspended by administration."}
            )

        if auth_acc.account_status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_INACTIVE", "message": "Account is not active."}
            )

        # Update last login
        auth_acc.last_login_at = datetime.now(timezone.utc)
        db.commit()

        access_token = create_access_token(
            subject=student.roll_no,
            role=auth_acc.role,
            token_version=auth_acc.token_version
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            roll_no=student.roll_no,
            name=student.name,
            role=auth_acc.role,
            account_status=auth_acc.account_status
        )

    @classmethod
    def get_me(cls, student: Student) -> UserMeResponse:
        auth_acc = student.auth_account
        return UserMeResponse(
            roll_no=student.roll_no,
            name=student.name,
            email=student.email,
            phone=student.phone,
            d_id=student.d_id,
            department_name=student.department.name if student.department else None,
            program=student.program,
            admission_year=student.admission_year,
            reputation_points=student.reputation_points,
            role=auth_acc.role,
            account_status=auth_acc.account_status,
            email_verified=auth_acc.email_verified,
            created_at=student.created_at
        )
