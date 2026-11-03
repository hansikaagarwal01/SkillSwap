from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user, require_admin
from app.models.skill import Skill
from app.models.department import Department
from app.models.student import Student
from app.schemas.skill import SkillCreate, SkillResponse

router = APIRouter(tags=["Skills & Departments"])

@router.get(
    "/skills",
    response_model=list[SkillResponse],
    summary="Get catalog of available skills"
)
def get_skills(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.name.asc()).all()

@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill in catalog (Admin or verified student)"
)
def create_skill(
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_active_user)
):
    existing = db.query(Skill).filter(Skill.name.ilike(skill_in.name.strip())).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "SKILL_EXISTS", "message": "A skill with this name already exists."}
        )

    new_skill = Skill(
        name=skill_in.name.strip(),
        category=skill_in.category.strip(),
        description=skill_in.description.strip() if skill_in.description else None
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

from app.models.department import PREDEFINED_DEPARTMENTS

@router.get(
    "/departments",
    summary="Get list of university academic departments"
)
def get_departments():
    return [{"d_id": d.d_id, "name": d.name, "program": d.program} for d in PREDEFINED_DEPARTMENTS]

