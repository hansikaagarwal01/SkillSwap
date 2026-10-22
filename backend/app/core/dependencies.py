from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.student import Student
from app.models.auth import AuthAccount

limiter = Limiter(key_func=get_remote_address)
security_scheme = HTTPBearer(auto_error=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Student:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing authentication credentials."}
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired access token."}
        )
    
    roll_no: str = payload.get("sub")
    token_version: int = payload.get("token_version", 1)
    
    if not roll_no:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Malformed token payload."}
        )

    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student or not student.auth_account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User associated with this token does not exist."}
        )
    
    if student.auth_account.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_REVOKED", "message": "Token version invalidated. Please log in again."}
        )
    
    return student

def get_current_active_user(
    current_user: Student = Depends(get_current_user)
) -> Student:
    account = current_user.auth_account
    if not account.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "EMAIL_UNVERIFIED", "message": "Email has not been verified."}
        )
    if account.account_status == "UNVERIFIED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_UNVERIFIED", "message": "Account is unverified."}
        )
    if account.account_status == "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PENDING_APPROVAL", "message": "Account pending administrator approval."}
        )
    if account.account_status == "SUSPENDED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_SUSPENDED", "message": "Account has been suspended."}
        )
    if account.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "Account is not active."}
        )
    return current_user

def require_admin(
    current_user: Student = Depends(get_current_active_user)
) -> Student:
    if current_user.auth_account.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ADMIN_REQUIRED", "message": "Administrator privileges required."}
        )
    return current_user
