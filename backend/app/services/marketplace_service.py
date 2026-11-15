from decimal import Decimal
from math import ceil
from typing import Optional, List, Dict, Any
from sqlalchemy import text, func, desc
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.student import Student
from app.models.session import LearningSession
from app.models.review import Review
from app.models.skill import Skill, StudentSkill, StudentDesiredSkill
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.common import PageResponse
from app.schemas.analytics import (
    LeaderboardEntry,
    AnalyticsOverview,
    ProgramDistributionItem,
    SessionStatusItem,
    TopSkillItem,
    MarketplaceStats,
)


def _to_listing_response(listing: Listing) -> ListingResponse:
    return ListingResponse(
        listing_id=listing.listing_id,
        seller_roll_no=listing.seller_roll_no,
        seller_name=listing.seller.name if listing.seller else None,
        seller_email=listing.seller.email if listing.seller else None,
        buyer_roll_no=listing.buyer_roll_no,
        buyer_name=listing.buyer.name if listing.buyer else None,
        buyer_email=listing.buyer.email if listing.buyer else None,
        title=listing.title,
        description=listing.description,
        status=listing.status,
        price=listing.price,
        original_price_text=listing.original_price_text,
        category=listing.category,
        item_condition=listing.item_condition,
        posted_date=listing.posted_date,
        sold_at=listing.sold_at,
    )


def create_listing(db: Session, seller_roll_no: str, data: ListingCreate) -> ListingResponse:
    student = db.query(Student).filter(Student.roll_no == seller_roll_no).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student seller not found")

    new_listing = Listing(
        seller_roll_no=seller_roll_no,
        title=data.title,
        description=data.description,
        price=data.price,
        category=data.category,
        item_condition=data.item_condition,
        status="AVAILABLE",
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return _to_listing_response(new_listing)


def get_listing_categories(db: Session) -> List[str]:
    rows = db.query(Listing.category).distinct().order_by(Listing.category.asc()).all()
    return [r[0] for r in rows if r[0]]


def get_listing_by_id(db: Session, listing_id: int) -> ListingResponse:
    listing = (
        db.query(Listing)
        .options(
            joinedload(Listing.seller),
            joinedload(Listing.buyer)
        )
        .filter(Listing.listing_id == listing_id)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return _to_listing_response(listing)


def list_listings(
    db: Session,
    category: Optional[str] = None,
    item_condition: Optional[str] = None,
    item_status: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[ListingResponse]:
    query = db.query(Listing).options(
        joinedload(Listing.seller),
        joinedload(Listing.buyer)
    )

    if category:
        query = query.filter(Listing.category == category)
    if item_condition:
        query = query.filter(Listing.item_condition == item_condition)
    if item_status:
        query = query.filter(Listing.status == item_status)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Listing.title.ilike(search_filter)) | (Listing.description.ilike(search_filter))
        )

    total = query.count()
    listings = (
        query.order_by(desc(Listing.posted_date))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = ceil(total / page_size) if total > 0 else 1
    items = [_to_listing_response(l) for l in listings]
    return PageResponse[ListingResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def update_listing(
    db: Session,
    listing_id: int,
    current_user_roll: str,
    is_admin: bool,
    data: ListingUpdate,
) -> ListingResponse:
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_roll_no != current_user_roll and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this listing",
        )

    if listing.status == "SOLD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a listing that has already been sold",
        )

    if listing.status == "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a listing while a purchase deal is in progress. Cancel the deal first.",
        )

    update_dict = data.model_dump(exclude_unset=True)
    if "status" in update_dict and update_dict["status"] in ("SOLD", "IN_PROGRESS"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status transitions to IN_PROGRESS or SOLD must use the purchase/confirmation endpoints.",
        )

    if "price" in update_dict and update_dict["price"] is not None and update_dict["price"] != listing.price:
        listing.original_price_text = None

    for field, value in update_dict.items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)
    return _to_listing_response(listing)


def delete_listing(
    db: Session,
    listing_id: int,
    current_user_roll: str,
    is_admin: bool,
) -> None:
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_roll_no != current_user_roll and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this listing",
        )

    if listing.status == "SOLD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a listing that has already been sold",
        )

    if listing.status == "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a listing while a purchase deal is in progress. Cancel the deal first.",
        )

    db.delete(listing)
    db.commit()


def purchase_listing(db: Session, listing_id: int, buyer_roll: str) -> ListingResponse:
    """
    Safe Concurrency Purchase Initiation:
    Executes conditional atomic update reserving the item for the buyer:
    UPDATE listing 
    SET status='IN_PROGRESS', buyer_roll_no=:buyer 
    WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer
    """
    stmt = text(
        """
        UPDATE listing 
        SET status = 'IN_PROGRESS', buyer_roll_no = :buyer 
        WHERE listing_id = :id AND status = 'AVAILABLE' AND seller_roll_no <> :buyer
        """
    )
    result = db.execute(stmt, {"id": listing_id, "buyer": buyer_roll})
    db.commit()

    if result.rowcount == 0:
        # Investigate root cause of failure for accurate client feedback
        listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
        if not listing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        if listing.seller_roll_no == buyer_roll:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot purchase your own listing",
            )
        if listing.status == "IN_PROGRESS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This listing is currently in progress with another buyer",
            )
        if listing.status == "SOLD":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This listing has already been sold to another student",
            )
        if listing.status == "REMOVED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This listing has been removed by the seller",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase could not be completed due to a concurrent update",
        )

    updated_listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    return _to_listing_response(updated_listing)


def confirm_sale(
    db: Session,
    listing_id: int,
    seller_roll: str,
    is_admin: bool = False,
) -> ListingResponse:
    """
    Seller confirms receipt of payment and final item handover:
    Transitions status from IN_PROGRESS to SOLD, setting sold_at = NOW().
    """
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_roll_no != seller_roll and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the seller can confirm receipt of payment and finalize the sale",
        )

    if listing.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm sale for listing with status '{listing.status}'. Must be 'IN_PROGRESS'.",
        )

    stmt = text(
        """
        UPDATE listing 
        SET status = 'SOLD', sold_at = NOW() 
        WHERE listing_id = :id AND status = 'IN_PROGRESS'
        """
    )
    db.execute(stmt, {"id": listing_id})
    db.commit()

    db.refresh(listing)
    return _to_listing_response(listing)


def cancel_sale(
    db: Session,
    listing_id: int,
    user_roll: str,
    is_admin: bool = False,
) -> ListingResponse:
    """
    Cancels an in-progress transaction, returning the listing to AVAILABLE status and clearing buyer_roll_no.
    Allowed by the buyer, the seller, or an administrator.
    """
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    if listing.seller_roll_no != user_roll and listing.buyer_roll_no != user_roll and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the buyer, seller, or an administrator can cancel this purchase",
        )

    if listing.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel purchase for listing with status '{listing.status}'. Must be 'IN_PROGRESS'.",
        )

    stmt = text(
        """
        UPDATE listing 
        SET status = 'AVAILABLE', buyer_roll_no = NULL, sold_at = NULL 
        WHERE listing_id = :id AND status = 'IN_PROGRESS'
        """
    )
    db.execute(stmt, {"id": listing_id})
    db.commit()

    db.refresh(listing)
    return _to_listing_response(listing)


def get_my_listings(
    db: Session,
    roll_no: str,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[ListingResponse]:
    query = (
        db.query(Listing)
        .options(
            joinedload(Listing.seller),
            joinedload(Listing.buyer)
        )
        .filter(Listing.seller_roll_no == roll_no)
    )
    total = query.count()
    listings = (
        query.order_by(desc(Listing.posted_date))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    items = [_to_listing_response(l) for l in listings]
    return PageResponse[ListingResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_my_purchases(
    db: Session,
    roll_no: str,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[ListingResponse]:
    query = (
        db.query(Listing)
        .options(
            joinedload(Listing.seller),
            joinedload(Listing.buyer)
        )
        .filter(Listing.buyer_roll_no == roll_no)
    )
    total = query.count()
    listings = (
        query.order_by(desc(Listing.sold_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    items = [_to_listing_response(l) for l in listings]
    return PageResponse[ListingResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_leaderboard(db: Session, limit: int = 20) -> List[LeaderboardEntry]:
    """
    Retrieves student leaderboard ranked by reputation points using MySQL DENSE_RANK().
    """
    query = text(
        """
        SELECT 
            DENSE_RANK() OVER (ORDER BY s.reputation_points DESC) AS rank_pos,
            s.roll_no,
            s.name,
            s.program,
            s.reputation_points,
            (SELECT COUNT(*) FROM learning_session ls WHERE ls.mentor_roll_no = s.roll_no AND ls.status = 'COMPLETED') AS sessions_mentored,
            (SELECT ROUND(AVG(r.rating), 2) FROM review r WHERE r.reviewee_roll_no = s.roll_no) AS avg_rating
        FROM student s
        ORDER BY s.reputation_points DESC, s.roll_no ASC
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"limit": limit}).fetchall()
    leaderboard = []
    for r in rows:
        leaderboard.append(
            LeaderboardEntry(
                rank=r[0],
                roll_no=r[1],
                name=r[2],
                program=r[3],
                reputation_points=r[4],
                sessions_mentored=r[5],
                avg_rating=float(r[6]) if r[6] is not None else None,
            )
        )
    return leaderboard


def get_analytics_overview(db: Session) -> AnalyticsOverview:
    total_students = db.query(func.count(Student.roll_no)).scalar() or 0
    total_skills = db.query(func.count(Skill.skill_id)).scalar() or 0
    total_sessions = db.query(func.count(LearningSession.session_id)).scalar() or 0
    total_listings = db.query(func.count(Listing.listing_id)).scalar() or 0
    total_desired_skills = db.query(func.count(StudentDesiredSkill.roll_no)).scalar() or 0

    # 1. Program-wise distribution (Query 27)
    prog_rows = db.execute(
        text(
            """
            SELECT s.program,
                   COUNT(s.roll_no) AS student_count,
                   COALESCE(SUM(s.reputation_points), 0) AS total_reputation,
                   ROUND(COALESCE(AVG(s.reputation_points), 0), 2) AS avg_reputation
            FROM student s
            GROUP BY s.program
            ORDER BY student_count DESC
            """
        )
    ).fetchall()
    programs = [
        ProgramDistributionItem(
            program=r[0],
            student_count=r[1],
            total_reputation=int(r[2]),
            avg_reputation=float(r[3]),
        )
        for r in prog_rows
    ]

    # 2. Session status breakdown (Query 28)
    status_rows = db.execute(
        text(
            """
            SELECT ls.status,
                   COUNT(ls.session_id) AS session_count,
                   ROUND(COUNT(ls.session_id) * 100.0 / GREATEST((SELECT COUNT(*) FROM learning_session), 1), 1) AS percentage_share
            FROM learning_session ls
            GROUP BY ls.status
            ORDER BY session_count DESC
            """
        )
    ).fetchall()
    session_statuses = [
        SessionStatusItem(
            status=r[0],
            session_count=r[1],
            percentage_share=float(r[2]),
        )
        for r in status_rows
    ]

    # 3. Top skills by learner/mentor count
    top_skill_rows = db.execute(
        text(
            """
            SELECT sk.skill_id, sk.name, sk.category, COUNT(ss.roll_no) AS student_count
            FROM skill sk
            LEFT JOIN student_skill ss ON sk.skill_id = ss.skill_id
            GROUP BY sk.skill_id, sk.name, sk.category
            ORDER BY student_count DESC, sk.name ASC
            LIMIT 5
            """
        )
    ).fetchall()
    top_skills = [
        TopSkillItem(
            skill_id=r[0],
            name=r[1],
            category=r[2],
            student_count=r[3],
        )
        for r in top_skill_rows
    ]

    # 4. Marketplace volume & inventory
    available_count = (
        db.query(func.count(Listing.listing_id))
        .filter(Listing.status == "AVAILABLE")
        .scalar()
        or 0
    )
    sold_count = (
        db.query(func.count(Listing.listing_id))
        .filter(Listing.status == "SOLD")
        .scalar()
        or 0
    )
    total_vol = (
        db.query(func.coalesce(func.sum(Listing.price), 0))
        .filter(Listing.status == "SOLD")
        .scalar()
        or 0.0
    )
    marketplace = MarketplaceStats(
        total_listings=total_listings,
        available_listings=available_count,
        sold_listings=sold_count,
        total_volume=float(total_vol),
    )

    return AnalyticsOverview(
        total_students=total_students,
        total_skills=total_skills,
        total_sessions=total_sessions,
        total_listings=total_listings,
        total_desired_skills=total_desired_skills,
        programs=programs,
        session_statuses=session_statuses,
        top_skills=top_skills,
        marketplace=marketplace,
    )
