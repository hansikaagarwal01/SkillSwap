from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, limiter, get_current_user, require_admin
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserMeResponse
)
from app.models.student import Student

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new JKLU student account"
)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register(db, body)

@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify student email with cryptographically generated token"
)
@limiter.limit("10/minute")
def verify_email(request: Request, body: VerifyEmailRequest, db: Session = Depends(get_db)):
    return AuthService.verify_email(db, body.token)

@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="Resend verification email to unverified address"
)
@limiter.limit("3/minute")
def resend_verification(request: Request, body: ResendVerificationRequest, db: Session = Depends(get_db)):
    return AuthService.resend_verification(db, body.email)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with Roll Number and password"
)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, body)

@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get authenticated student identity and profile"
)
def get_me(current_user: Student = Depends(get_current_user)):
    return AuthService.get_me(current_user)


admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.post(
    "/accounts/{roll_no}/approve",
    status_code=status.HTTP_200_OK,
    summary="Approve a pending account (Admin only)"
)
@admin_router.post(
    "/approve/{roll_no}",
    status_code=status.HTTP_200_OK,
    summary="Approve a pending account alias"
)
def approve_account(
    roll_no: str,
    db: Session = Depends(get_db),
    admin: Student = Depends(require_admin)
):
    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ACCOUNT_NOT_FOUND", "message": "Account not found."}
        )
    if student.account_status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": f"Account status is {student.account_status}, not PENDING_APPROVAL."}
        )
    student.account_status = "ACTIVE"
    db.commit()
    return {"message": f"Account {roll_no} successfully approved and activated."}
