from typing import Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status
from math import ceil

from app.models.student import Student
from app.models.department import Department
from app.models.skill import Skill, StudentSkill
from app.models.session import LearningSession
from app.models.review import Review
from app.schemas.student import (
    StudentUpdate,
    StudentResponse,
    StudentSkillCreate,
    StudentSkillResponse,
    MentorResponse
)
from app.schemas.common import PageResponse

PROFICIENCY_WEIGHTS = {
    "BEGINNER": 1,
    "INTERMEDIATE": 2,
    "ADVANCED": 3,
    "EXPERT": 4
}

class StudentService:
    @staticmethod
    def list_students(
        db: Session,
        program: Optional[str] = None,
        admission_year: Optional[int] = None,
        skill_id: Optional[int] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PageResponse[StudentResponse]:
        query = db.query(Student)

        if program:
            query = query.filter(Student.program == program.upper())
        if admission_year:
            query = query.filter(Student.admission_year == admission_year)
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(or_(Student.name.ilike(term), Student.roll_no.ilike(term)))
        if skill_id:
            query = query.join(StudentSkill, Student.roll_no == StudentSkill.roll_no).filter(StudentSkill.skill_id == skill_id)

        total = query.count()
        total_pages = ceil(total / page_size) if total > 0 else 1
        students = query.order_by(Student.roll_no.asc()).offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for s in students:
            skills_resp = [
                StudentSkillResponse(
                    roll_no=ss.roll_no,
                    skill_id=ss.skill_id,
                    skill_name=ss.skill.name if ss.skill else None,
                    category=ss.skill.category if ss.skill else None,
                    proficiency_level=ss.proficiency_level,
                    can_teach=ss.can_teach,
                    created_at=ss.created_at
                )
                for ss in s.skills
            ]
            items.append(
                StudentResponse(
                    roll_no=s.roll_no,
                    name=s.name,
                    email=s.email,
                    phone=s.phone,
                    d_id=s.d_id,
                    department_name=s.department.name if s.department else None,
                    program=s.program,
                    admission_year=s.admission_year,
                    reputation_points=s.reputation_points,
                    created_at=s.created_at,
                    skills=skills_resp
                )
            )

        return PageResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def get_student(db: Session, roll_no: str) -> StudentResponse:
        s = db.query(Student).filter(Student.roll_no == roll_no).first()
        if not s:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "STUDENT_NOT_FOUND", "message": f"Student with roll number {roll_no} was not found."}
            )

        skills_resp = [
            StudentSkillResponse(
                roll_no=ss.roll_no,
                skill_id=ss.skill_id,
                skill_name=ss.skill.name if ss.skill else None,
                category=ss.skill.category if ss.skill else None,
                proficiency_level=ss.proficiency_level,
                can_teach=ss.can_teach,
                created_at=ss.created_at
            )
            for ss in s.skills
        ]

        return StudentResponse(
            roll_no=s.roll_no,
            name=s.name,
            email=s.email,
            phone=s.phone,
            d_id=s.d_id,
            department_name=s.department.name if s.department else None,
            program=s.program,
            admission_year=s.admission_year,
            reputation_points=s.reputation_points,
            created_at=s.created_at,
            skills=skills_resp
        )

    @staticmethod
    def update_student(
        db: Session,
        roll_no: str,
        update_data: StudentUpdate,
        current_user: Student
    ) -> StudentResponse:
        # Authorization check: only owner or ADMIN
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "You are not authorized to edit another student's profile."}
            )

        student = db.query(Student).filter(Student.roll_no == roll_no).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "STUDENT_NOT_FOUND", "message": f"Student {roll_no} not found."}
            )

        if update_data.name is not None:
            student.name = update_data.name
        if update_data.phone is not None:
            student.phone = update_data.phone
        if update_data.d_id is not None:
            dept = db.query(Department).filter(Department.d_id == update_data.d_id).first()
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "DEPARTMENT_NOT_FOUND", "message": "Specified department does not exist."}
                )
            student.d_id = update_data.d_id

        db.commit()
        db.refresh(student)
        return StudentService.get_student(db, roll_no)

    @staticmethod
    def get_student_skills(db: Session, roll_no: str) -> list[StudentSkillResponse]:
        student = db.query(Student).filter(Student.roll_no == roll_no).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "STUDENT_NOT_FOUND", "message": f"Student {roll_no} not found."}
            )

        return [
            StudentSkillResponse(
                roll_no=ss.roll_no,
                skill_id=ss.skill_id,
                skill_name=ss.skill.name if ss.skill else None,
                category=ss.skill.category if ss.skill else None,
                proficiency_level=ss.proficiency_level,
                can_teach=ss.can_teach,
                created_at=ss.created_at
            )
            for ss in student.skills
        ]

    @staticmethod
    def add_or_update_student_skill(
        db: Session,
        roll_no: str,
        skill_in: StudentSkillCreate,
        current_user: Student
    ) -> StudentSkillResponse:
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot modify skills of another student."}
            )

        skill = db.query(Skill).filter(Skill.skill_id == skill_in.skill_id).first()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SKILL_NOT_FOUND", "message": "Skill not found in catalog."}
            )

        existing = db.query(StudentSkill).filter(
            StudentSkill.roll_no == roll_no,
            StudentSkill.skill_id == skill_in.skill_id
        ).first()

        if existing:
            existing.proficiency_level = skill_in.proficiency_level
            existing.can_teach = skill_in.can_teach
            db.commit()
            db.refresh(existing)
            target = existing
        else:
            new_ss = StudentSkill(
                roll_no=roll_no,
                skill_id=skill_in.skill_id,
                proficiency_level=skill_in.proficiency_level,
                can_teach=skill_in.can_teach
            )
            db.add(new_ss)
            db.commit()
            db.refresh(new_ss)
            target = new_ss

        return StudentSkillResponse(
            roll_no=target.roll_no,
            skill_id=target.skill_id,
            skill_name=skill.name,
            category=skill.category,
            proficiency_level=target.proficiency_level,
            can_teach=target.can_teach,
            created_at=target.created_at
        )

    @staticmethod
    def delete_student_skill(
        db: Session,
        roll_no: str,
        skill_id: int,
        current_user: Student
    ) -> dict[str, str]:
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot remove skills of another student."}
            )

        record = db.query(StudentSkill).filter(
            StudentSkill.roll_no == roll_no,
            StudentSkill.skill_id == skill_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Skill mapping not found."}
            )

        db.delete(record)
        db.commit()
        return {"message": "Skill removed successfully from your profile."}

    @staticmethod
    def discover_mentors(
        db: Session,
        skill_id: Optional[int] = None,
        min_proficiency: Optional[str] = None,
        min_rating: Optional[float] = None,
        program: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PageResponse[MentorResponse]:
        # Query mentors with can_teach = True
        query = db.query(
            Student,
            StudentSkill,
            Skill,
            Department
        ).join(
            StudentSkill, Student.roll_no == StudentSkill.roll_no
        ).join(
            Skill, StudentSkill.skill_id == Skill.skill_id
        ).join(
            Department, Student.d_id == Department.d_id
        ).filter(
            StudentSkill.can_teach == True
        )

        if skill_id:
            query = query.filter(StudentSkill.skill_id == skill_id)
        if program:
            query = query.filter(Student.program == program.upper())

        rows = query.all()
        mentor_results: list[MentorResponse] = []

        min_weight = PROFICIENCY_WEIGHTS.get(min_proficiency.upper(), 0) if min_proficiency else 0

        for student, student_skill, skill, dept in rows:
            # Proficiency filter
            current_weight = PROFICIENCY_WEIGHTS.get(student_skill.proficiency_level, 0)
            if current_weight < min_weight:
                continue

            # Calculate average review rating for this mentor on completed sessions
            ratings_query = db.query(
                func.avg(Review.rating),
                func.count(Review.rating)
            ).join(
                LearningSession, Review.session_id == LearningSession.session_id
            ).filter(
                Review.reviewee_roll_no == student.roll_no,
                LearningSession.mentor_roll_no == student.roll_no,
                LearningSession.status == "COMPLETED"
            ).first()

            avg_rating = float(ratings_query[0]) if ratings_query[0] is not None else None
            review_count = int(ratings_query[1]) if ratings_query[1] else 0

            # Rating filter
            if min_rating is not None and (avg_rating is None or avg_rating < min_rating):
                continue

            # Completed sessions count
            comp_count = db.query(func.count(LearningSession.session_id)).filter(
                LearningSession.mentor_roll_no == student.roll_no,
                LearningSession.status == "COMPLETED"
            ).scalar() or 0

            mentor_results.append(
                MentorResponse(
                    roll_no=student.roll_no,
                    name=student.name,
                    email=student.email,
                    program=student.program,
                    admission_year=student.admission_year,
                    reputation_points=student.reputation_points,
                    department_name=dept.name,
                    skill_id=skill.skill_id,
                    skill_name=skill.name,
                    proficiency_level=student_skill.proficiency_level,
                    avg_rating=round(avg_rating, 2) if avg_rating else None,
                    total_reviews=review_count,
                    completed_sessions=comp_count
                )
            )

        # Sort by reputation DESC, rating DESC
        mentor_results.sort(
            key=lambda m: (m.reputation_points, m.avg_rating or 0.0),
            reverse=True
        )

        total = len(mentor_results)
        total_pages = ceil(total / page_size) if total > 0 else 1
        paged_items = mentor_results[(page - 1) * page_size : page * page_size]

        return PageResponse(
            items=paged_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
