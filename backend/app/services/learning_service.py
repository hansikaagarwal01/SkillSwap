from datetime import datetime, timezone
from typing import Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, select
from fastapi import HTTPException, status
from math import ceil

from app.core.config import settings
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.session import LearningSession
from app.models.review import Review
from app.models.experience import Experience
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionReschedule,
    SessionStatusUpdate,
    SessionResponse,
    ReviewCreate,
    ReviewResponse
)
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from app.schemas.common import PageResponse

class LearningService:
    # -------------------------------------------------------------------------
    # SESSION MANAGEMENT
    # -------------------------------------------------------------------------
    @staticmethod
    def create_session(
        db: Session,
        req: SessionCreate,
        current_user: Student
    ) -> SessionResponse:
        learner_roll = current_user.roll_no
        mentor_roll = req.mentor_roll_no.upper()

        if learner_roll == mentor_roll:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "SELF_MENTORING_BLOCKED", "message": "You cannot request a mentoring session with yourself."}
            )

        mentor = db.query(Student).filter(Student.roll_no == mentor_roll).first()
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "MENTOR_NOT_FOUND", "message": f"Mentor {mentor_roll} not found."}
            )

        # Verify mentor possesses this skill
        teaching_skill = db.query(StudentSkill).filter(
            StudentSkill.roll_no == mentor_roll,
            StudentSkill.skill_id == req.skill_id
        ).first()

        if not teaching_skill:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "SKILL_NOT_TAUGHT", "message": "Mentor is not registered to teach this skill."}
            )

        new_session = LearningSession(
            mentor_roll_no=mentor_roll,
            learner_roll_no=learner_roll,
            skill_id=req.skill_id,
            topic=req.topic,
            mode=req.mode,
            scheduled_at=req.scheduled_at,
            meeting_link=req.meeting_link,
            status="REQUESTED",
            credit_cost=0
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return LearningService.to_session_response(new_session, current_user.roll_no)

    @staticmethod
    def get_session(
        db: Session,
        session_id: int,
        current_user: Student
    ) -> SessionResponse:
        session = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )
        return LearningService.to_session_response(session, current_user.roll_no)

    @staticmethod
    def list_sessions(
        db: Session,
        current_user: Student,
        session_status: Optional[str] = None,
        role: Optional[Literal["MENTOR", "LEARNER"]] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PageResponse[SessionResponse]:
        roll = current_user.roll_no
        query = db.query(LearningSession)

        if role == "MENTOR":
            query = query.filter(LearningSession.mentor_roll_no == roll)
        elif role == "LEARNER":
            query = query.filter(LearningSession.learner_roll_no == roll)
        else:
            query = query.filter(
                or_(
                    LearningSession.mentor_roll_no == roll,
                    LearningSession.learner_roll_no == roll
                )
            )

        if session_status:
            query = query.filter(LearningSession.status == session_status.upper())

        total = query.count()
        total_pages = ceil(total / page_size) if total > 0 else 1
        sessions = query.order_by(LearningSession.scheduled_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        items = [LearningService.to_session_response(s, roll) for s in sessions]
        return PageResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def update_session_status(
        db: Session,
        session_id: int,
        new_status: str,
        current_user: Student
    ) -> SessionResponse:
        new_status = new_status.upper()
        user_roll = current_user.roll_no

        if new_status == "COMPLETED":
            return LearningService.complete_session_transaction(db, session_id, current_user)

        session = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )

        is_mentor = (session.mentor_roll_no == user_roll)
        is_learner = (session.learner_roll_no == user_roll)
        is_admin = (current_user.auth_account.role == "ADMIN")

        if not (is_mentor or is_learner or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "You are not a participant in this session."}
            )

        current_st = session.status

        # State machine validations
        if current_st == "REQUESTED":
            if new_status == "ACCEPTED":
                if not (is_mentor or is_admin):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={"code": "MENTOR_ONLY", "message": "Only the mentor can accept a session request."}
                    )
            elif new_status == "REJECTED":
                if not (is_mentor or is_admin):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={"code": "MENTOR_ONLY", "message": "Only the mentor can reject a session request."}
                    )
            elif new_status == "CANCELLED":
                if not (is_learner or is_admin):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={"code": "LEARNER_ONLY", "message": "Only the learner can cancel a requested session."}
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "INVALID_TRANSITION", "message": f"Cannot transition session from REQUESTED to {new_status}."}
                )

        elif current_st == "ACCEPTED":
            if new_status == "CANCELLED":
                pass # Either participant can cancel an accepted session
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "INVALID_TRANSITION", "message": f"Cannot transition session from ACCEPTED to {new_status} via standard update."}
                )

        elif current_st in ("COMPLETED", "REJECTED", "CANCELLED"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "TERMINAL_STATE", "message": f"Cannot modify a session that is already in terminal state {current_st}."}
            )

        session.status = new_status
        db.commit()
        db.refresh(session)
        return LearningService.to_session_response(session, user_roll)

    @staticmethod
    def complete_session_transaction(
        db: Session,
        session_id: int,
        current_user: Student
    ) -> SessionResponse:
        user_roll = current_user.roll_no

        # Begin transaction and acquire row lock with SELECT ... FOR UPDATE
        session = db.query(LearningSession).filter(
            LearningSession.session_id == session_id
        ).with_for_update().first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )

        is_mentor = (session.mentor_roll_no == user_roll)
        is_admin = (current_user.auth_account.role == "ADMIN")
        if not (is_mentor or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "MENTOR_ONLY", "message": "Only the mentor can mark a session as completed."}
            )

        if session.status == "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "ALREADY_COMPLETED", "message": "Session is already completed. Reputation reward was already credited."}
            )

        if session.status != "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "INVALID_STATE", "message": f"Only ACCEPTED sessions can be completed (current status: {session.status})."}
            )

        # Check scheduled_at <= now
        now = datetime.now(timezone.utc)
        sched = session.scheduled_at
        if sched.tzinfo is None:
            sched = sched.replace(tzinfo=timezone.utc)

        if sched > now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "PREMATURE_COMPLETION", "message": "Cannot complete a session before its scheduled time."}
            )

        try:
            # 1. Update session status and record reputation reward audit
            session.status = "COMPLETED"
            session.reputation_awarded = True
            session.points_awarded = settings.REPUTATION_PER_SESSION
            session.reputation_awarded_at = datetime.now(timezone.utc)

            # 2. Increment mentor's reputation points
            mentor = db.query(Student).filter(Student.roll_no == session.mentor_roll_no).with_for_update().first()
            if mentor:
                mentor.reputation_points += settings.REPUTATION_PER_SESSION

            db.commit()
            db.refresh(session)
            return LearningService.to_session_response(session, user_roll)

        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def reschedule_session(
        db: Session,
        session_id: int,
        req: SessionReschedule,
        current_user: Student
    ) -> SessionResponse:
        user_roll = current_user.roll_no
        session = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )

        is_mentor = (session.mentor_roll_no == user_roll)
        is_learner = (session.learner_roll_no == user_roll)
        is_admin = (current_user.auth_account.role == "ADMIN")

        if not (is_mentor or is_learner or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "You are not a participant in this session."}
            )

        if session.status not in ("REQUESTED", "ACCEPTED"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "CANNOT_RESCHEDULE", "message": f"Sessions in status {session.status} cannot be rescheduled."}
            )

        session.scheduled_at = req.scheduled_at
        # Returning to REQUESTED pending other party acceptance
        session.status = "REQUESTED"
        db.commit()
        db.refresh(session)
        return LearningService.to_session_response(session, user_roll)

    @staticmethod
    def update_session(
        db: Session,
        session_id: int,
        req: SessionUpdate,
        current_user: Student
    ) -> SessionResponse:
        user_roll = current_user.roll_no
        session = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )

        is_mentor = (session.mentor_roll_no == user_roll)
        is_learner = (session.learner_roll_no == user_roll)
        is_admin = (current_user.auth_account.role == "ADMIN")

        if not (is_mentor or is_learner or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "You are not a participant in this session."}
            )

        if session.status in ("COMPLETED", "CANCELLED", "REJECTED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "SESSION_CLOSED", "message": f"Cannot edit a session that is {session.status}."}
            )

        if req.topic is not None:
            session.topic = req.topic
        if req.mode is not None:
            session.mode = req.mode
        if req.scheduled_at is not None:
            session.scheduled_at = req.scheduled_at
        if req.meeting_link is not None:
            session.meeting_link = req.meeting_link

        db.commit()
        db.refresh(session)
        return LearningService.to_session_response(session, user_roll)

    # -------------------------------------------------------------------------
    # REVIEWS
    # -------------------------------------------------------------------------
    @staticmethod
    def create_review(
        db: Session,
        req: ReviewCreate,
        current_user: Student
    ) -> ReviewResponse:
        reviewer_roll = current_user.roll_no

        session = db.query(LearningSession).filter(LearningSession.session_id == req.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."}
            )

        if session.status != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "SESSION_NOT_COMPLETED", "message": "Reviews can only be submitted for COMPLETED sessions."}
            )

        is_mentor = (session.mentor_roll_no == reviewer_roll)
        is_learner = (session.learner_roll_no == reviewer_roll)

        if not (is_mentor or is_learner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "NOT_PARTICIPANT", "message": "Only participants can review this session."}
            )

        # Reviewer reviews the other participant
        reviewee_roll = session.learner_roll_no if is_mentor else session.mentor_roll_no

        # Check duplicate review
        existing = db.query(Review).filter(
            Review.session_id == req.session_id,
            Review.roll_no == reviewer_roll
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "DUPLICATE_REVIEW", "message": "You have already submitted a review for this session."}
            )

        new_review = Review(
            session_id=req.session_id,
            roll_no=reviewer_roll,
            reviewee_roll_no=reviewee_roll,
            rating=req.rating,
            comment=req.comment
        )
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        return ReviewResponse(
            session_id=new_review.session_id,
            roll_no=new_review.roll_no,
            reviewer_name=current_user.name,
            reviewee_roll_no=new_review.reviewee_roll_no,
            reviewee_name=new_review.reviewee.name if new_review.reviewee else None,
            rating=new_review.rating,
            comment=new_review.comment,
            created_at=new_review.created_at
        )

    @staticmethod
    def get_session_reviews(db: Session, session_id: int) -> list[ReviewResponse]:
        reviews = db.query(Review).filter(Review.session_id == session_id).all()
        return [
            ReviewResponse(
                session_id=r.session_id,
                roll_no=r.roll_no,
                reviewer_name=r.reviewer.name if r.reviewer else None,
                reviewee_roll_no=r.reviewee_roll_no,
                reviewee_name=r.reviewee.name if r.reviewee else None,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at
            )
            for r in reviews
        ]

    # -------------------------------------------------------------------------
    # EXPERIENCES
    # -------------------------------------------------------------------------
    @staticmethod
    def list_experiences(db: Session, roll_no: str) -> list[ExperienceResponse]:
        exps = db.query(Experience).filter(
            Experience.roll_no == roll_no.upper()
        ).order_by(Experience.start_date.desc()).all()

        return [
            ExperienceResponse(
                roll_no=e.roll_no,
                exp_no=e.exp_no,
                role_title=e.role_title,
                organization=e.organization,
                exp_type=e.exp_type,
                start_date=e.start_date,
                end_date=e.end_date,
                description=e.description,
                created_at=e.created_at
            )
            for e in exps
        ]

    @staticmethod
    def create_experience(
        db: Session,
        roll_no: str,
        req: ExperienceCreate,
        current_user: Student
    ) -> ExperienceResponse:
        roll_no = roll_no.upper()
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot create experience for another student."}
            )

        # Transactionally determine next exp_no for this roll_no
        max_exp = db.query(func.coalesce(func.max(Experience.exp_no), 0)).filter(
            Experience.roll_no == roll_no
        ).scalar()
        next_exp_no = max_exp + 1

        new_exp = Experience(
            roll_no=roll_no,
            exp_no=next_exp_no,
            role_title=req.role_title,
            organization=req.organization,
            exp_type=req.exp_type,
            start_date=req.start_date,
            end_date=req.end_date,
            description=req.description
        )
        db.add(new_exp)
        db.commit()
        db.refresh(new_exp)

        return ExperienceResponse(
            roll_no=new_exp.roll_no,
            exp_no=new_exp.exp_no,
            role_title=new_exp.role_title,
            organization=new_exp.organization,
            exp_type=new_exp.exp_type,
            start_date=new_exp.start_date,
            end_date=new_exp.end_date,
            description=new_exp.description,
            created_at=new_exp.created_at
        )

    @staticmethod
    def update_experience(
        db: Session,
        roll_no: str,
        exp_no: int,
        req: ExperienceUpdate,
        current_user: Student
    ) -> ExperienceResponse:
        roll_no = roll_no.upper()
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot edit experience for another student."}
            )

        exp = db.query(Experience).filter(
            Experience.roll_no == roll_no,
            Experience.exp_no == exp_no
        ).first()

        if not exp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Experience entry not found."}
            )

        if req.role_title is not None:
            exp.role_title = req.role_title
        if req.organization is not None:
            exp.organization = req.organization
        if req.exp_type is not None:
            exp.exp_type = req.exp_type
        if req.start_date is not None:
            exp.start_date = req.start_date
        if req.end_date is not None:
            exp.end_date = req.end_date
        if req.description is not None:
            exp.description = req.description

        db.commit()
        db.refresh(exp)

        return ExperienceResponse(
            roll_no=exp.roll_no,
            exp_no=exp.exp_no,
            role_title=exp.role_title,
            organization=exp.organization,
            exp_type=exp.exp_type,
            start_date=exp.start_date,
            end_date=exp.end_date,
            description=exp.description,
            created_at=exp.created_at
        )

    @staticmethod
    def delete_experience(
        db: Session,
        roll_no: str,
        exp_no: int,
        current_user: Student
    ) -> dict[str, str]:
        roll_no = roll_no.upper()
        if current_user.roll_no != roll_no and current_user.auth_account.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Cannot delete experience for another student."}
            )

        exp = db.query(Experience).filter(
            Experience.roll_no == roll_no,
            Experience.exp_no == exp_no
        ).first()

        if not exp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Experience entry not found."}
            )

        db.delete(exp)
        db.commit()
        return {"message": "Experience removed successfully."}

    # -------------------------------------------------------------------------
    # HELPER
    # -------------------------------------------------------------------------
    @staticmethod
    def to_session_response(s: LearningSession, user_roll: str) -> SessionResponse:
        # Mask meeting link if not participant
        is_participant = (s.mentor_roll_no == user_roll or s.learner_roll_no == user_roll)
        link = s.meeting_link if is_participant else None

        has_rev = len(s.reviews) > 0 if s.reviews else False

        return SessionResponse(
            session_id=s.session_id,
            mentor_roll_no=s.mentor_roll_no,
            mentor_name=s.mentor.name if s.mentor else None,
            learner_roll_no=s.learner_roll_no,
            learner_name=s.learner.name if s.learner else None,
            skill_id=s.skill_id,
            skill_name=s.skill.name if s.skill else None,
            topic=s.topic,
            mode=s.mode,
            scheduled_at=s.scheduled_at,
            meeting_link=link,
            status=s.status,
            credit_cost=s.credit_cost,
            points_awarded=s.points_awarded,
            reputation_awarded=s.reputation_awarded,
            reputation_awarded_at=s.reputation_awarded_at,
            created_at=s.created_at,
            updated_at=s.updated_at,
            has_review=has_rev
        )
