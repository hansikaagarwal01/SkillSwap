from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.student import Student
from app.services.student_service import StudentService
from app.schemas.student import (
    StudentResponse,
    StudentUpdate,
    StudentSkillCreate,
    StudentSkillResponse,
    MentorResponse
)
from app.schemas.common import PageResponse

router = APIRouter(tags=["Students & Mentors"])

@router.get(
    "/students",
    response_model=PageResponse[StudentResponse],
    summary="List and filter students"
)
def list_students(
    program: Optional[Literal["BTECH", "BBA", "BDES"]] = Query(None, description="Academic program"),
    admission_year: Optional[int] = Query(None, description="Admission cohort year"),
    skill_id: Optional[int] = Query(None, description="Possessed skill ID"),
    q: Optional[str] = Query(None, description="Search by name or roll number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return StudentService.list_students(
        db=db,
        program=program,
        admission_year=admission_year,
        skill_id=skill_id,
        q=q,
        page=page,
        page_size=page_size
    )

@router.get(
    "/mentors",
    response_model=PageResponse[MentorResponse],
    summary="Discover peer mentors by skill, proficiency, rating, and program"
)
def discover_mentors(
    skill_id: Optional[int] = Query(None, description="Skill ID to find mentors for"),
    min_proficiency: Optional[Literal["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]] = Query(None),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    program: Optional[Literal["BTECH", "BBA", "BDES"]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return StudentService.discover_mentors(
        db=db,
        skill_id=skill_id,
        min_proficiency=min_proficiency,
        min_rating=min_rating,
        program=program,
        page=page,
        page_size=page_size
    )

@router.get(
    "/students/{roll_no}",
    response_model=StudentResponse,
    summary="Get detailed public profile of a student"
)
def get_student_profile(
    roll_no: str,
    db: Session = Depends(get_db)
):
    return StudentService.get_student(db, roll_no.upper())

@router.patch(
    "/students/{roll_no}",
    response_model=StudentResponse,
    summary="Update student profile (Owner only; roll_no and program immutable)"
)
def update_student_profile(
    roll_no: str,
    update_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return StudentService.update_student(
        db=db,
        roll_no=roll_no.upper(),
        update_data=update_data,
        current_user=current_user
    )

@router.get(
    "/students/{roll_no}/skills",
    response_model=list[StudentSkillResponse],
    summary="Get skills of a specific student"
)
def get_student_skills(
    roll_no: str,
    db: Session = Depends(get_db)
):
    return StudentService.get_student_skills(db, roll_no.upper())

@router.post(
    "/students/{roll_no}/skills",
    response_model=StudentSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or update a skill on student profile (Owner only)"
)
def add_or_update_student_skill(
    roll_no: str,
    skill_in: StudentSkillCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return StudentService.add_or_update_student_skill(
        db=db,
        roll_no=roll_no.upper(),
        skill_in=skill_in,
        current_user=current_user
    )

@router.delete(
    "/students/{roll_no}/skills/{skill_id}",
    summary="Remove a skill from student profile (Owner only)"
)
def delete_student_skill(
    roll_no: str,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    return StudentService.delete_student_skill(
        db=db,
        roll_no=roll_no.upper(),
        skill_id=skill_id,
        current_user=current_user
    )
