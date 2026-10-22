from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.student import Student
from app.services.learning_service import LearningService
from app.schemas.session import (
    SessionCreate,
    SessionReschedule,
    SessionStatusUpdate,
    SessionResponse,
    ReviewCreate,
    ReviewResponse
)
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from app.schemas.common import PageResponse

router = APIRouter(tags=["Learning Sessions, Reviews & Experiences"])

# --- Sessions ---
@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a new peer mentoring session"
)
def create_session(
    req: SessionCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.create_session(db, req, current_user)

@router.get(
    "/sessions",
    response_model=PageResponse[SessionResponse],
    summary="List sessions for the current authenticated user"
)
def list_sessions(
    status: Optional[Literal["REQUESTED", "ACCEPTED", "REJECTED", "CANCELLED", "COMPLETED"]] = Query(None),
    role: Optional[Literal["MENTOR", "LEARNER"]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.list_sessions(
        db=db,
        current_user=current_user,
        session_status=status,
        role=role,
        page=page,
        page_size=page_size
    )

@router.get(
    "/sessions/{id}",
    response_model=SessionResponse,
    summary="Get details of a learning session"
)
def get_session(
    id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.get_session(db, id, current_user)

@router.patch(
    "/sessions/{id}/status",
    response_model=SessionResponse,
    summary="Update session lifecycle status (ACCEPTED, REJECTED, CANCELLED, COMPLETED)"
)
def update_session_status(
    id: int,
    body: SessionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.update_session_status(db, id, body.status, current_user)

@router.patch(
    "/sessions/{id}/reschedule",
    response_model=SessionResponse,
    summary="Propose a new schedule time for a session"
)
def reschedule_session(
    id: int,
    body: SessionReschedule,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.reschedule_session(db, id, body, current_user)

# --- Reviews ---
@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a completed session"
)
def create_review(
    req: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.create_review(db, req, current_user)

@router.get(
    "/sessions/{id}/reviews",
    response_model=list[ReviewResponse],
    summary="Get all reviews submitted for a session"
)
def get_session_reviews(
    id: int,
    db: Session = Depends(get_db)
):
    return LearningService.get_session_reviews(db, id)

# --- Experiences ---
@router.get(
    "/students/{roll_no}/experiences",
    response_model=list[ExperienceResponse],
    summary="Get experience portfolio entries for a student"
)
def list_experiences(
    roll_no: str,
    db: Session = Depends(get_db)
):
    return LearningService.list_experiences(db, roll_no)

@router.post(
    "/students/{roll_no}/experiences",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an experience entry (Owner only)"
)
def create_experience(
    roll_no: str,
    req: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.create_experience(db, roll_no, req, current_user)

@router.patch(
    "/experiences/{roll_no}/{exp_no}",
    response_model=ExperienceResponse,
    summary="Update an experience entry (Owner only)"
)
def update_experience(
    roll_no: str,
    exp_no: int,
    req: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.update_experience(db, roll_no, exp_no, req, current_user)

@router.delete(
    "/experiences/{roll_no}/{exp_no}",
    summary="Delete an experience entry (Owner only)"
)
def delete_experience(
    roll_no: str,
    exp_no: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return LearningService.delete_experience(db, roll_no, exp_no, current_user)
