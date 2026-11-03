from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    roll_no: str
    name: str
    program: str
    reputation_points: int
    sessions_mentored: int
    avg_rating: Optional[float] = None


class ProgramDistributionItem(BaseModel):
    program: str
    student_count: int
    total_reputation: int
    avg_reputation: float


class SessionStatusItem(BaseModel):
    status: str
    session_count: int
    percentage_share: float


class TopSkillItem(BaseModel):
    skill_id: int
    name: str
    category: str
    student_count: int


class MarketplaceStats(BaseModel):
    total_listings: int
    available_listings: int
    sold_listings: int
    total_volume: float


class AnalyticsOverview(BaseModel):
    total_students: int
    total_skills: int
    total_sessions: int
    total_listings: int
    total_desired_skills: int = 0
    programs: List[ProgramDistributionItem]
    session_statuses: List[SessionStatusItem]
    top_skills: List[TopSkillItem]
    marketplace: MarketplaceStats
