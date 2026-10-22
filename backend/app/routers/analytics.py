from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import LeaderboardEntry, AnalyticsOverview
from app.services import marketplace_service

router = APIRouter(tags=["Analytics & Leaderboard"])


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    limit: int = Query(20, ge=1, le=100, description="Top N students"),
    db: Session = Depends(get_db),
):
    return marketplace_service.get_leaderboard(db=db, limit=limit)


@router.get("/analytics/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    db: Session = Depends(get_db),
):
    return marketplace_service.get_analytics_overview(db=db)
