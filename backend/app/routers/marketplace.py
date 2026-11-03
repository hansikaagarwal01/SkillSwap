from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_active_user
from app.models.student import Student
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.common import PageResponse
from app.services import marketplace_service

router = APIRouter(prefix="/listings", tags=["Marketplace"])


@router.get("", response_model=PageResponse[ListingResponse])
def list_listings(
    category: Optional[str] = Query(None, description="Filter by category"),
    item_condition: Optional[str] = Query(None, description="Filter by condition"),
    status: Optional[str] = Query(None, description="Filter by status (AVAILABLE, SOLD, REMOVED)"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    search: Optional[str] = Query(None, description="Keyword search in title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    return marketplace_service.list_listings(
        db=db,
        category=category,
        item_condition=item_condition,
        item_status=status,
        min_price=min_price,
        max_price=max_price,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return marketplace_service.create_listing(
        db=db,
        seller_roll_no=current_user.roll_no,
        data=payload,
    )


@router.get("/mine", response_model=PageResponse[ListingResponse])
def get_my_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return marketplace_service.get_my_listings(
        db=db,
        roll_no=current_user.roll_no,
        page=page,
        page_size=page_size,
    )


@router.get("/purchases", response_model=PageResponse[ListingResponse])
def get_my_purchases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return marketplace_service.get_my_purchases(
        db=db,
        roll_no=current_user.roll_no,
        page=page,
        page_size=page_size,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    return marketplace_service.get_listing_by_id(db=db, listing_id=listing_id)


@router.patch("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    is_admin = current_user.auth_account and current_user.auth_account.role == "ADMIN"
    return marketplace_service.update_listing(
        db=db,
        listing_id=listing_id,
        current_user_roll=current_user.roll_no,
        is_admin=is_admin,
        data=payload,
    )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    is_admin = current_user.auth_account and current_user.auth_account.role == "ADMIN"
    marketplace_service.delete_listing(
        db=db,
        listing_id=listing_id,
        current_user_roll=current_user.roll_no,
        is_admin=is_admin,
    )
    return None


@router.post("/{listing_id}/purchase", response_model=ListingResponse)
def purchase_listing(
    listing_id: int,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return marketplace_service.purchase_listing(
        db=db,
        listing_id=listing_id,
        buyer_roll=current_user.roll_no,
    )


@router.post("/{listing_id}/confirm-sale", response_model=ListingResponse)
def confirm_sale(
    listing_id: int,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    is_admin = bool(current_user.auth_account and current_user.auth_account.role == "ADMIN")
    return marketplace_service.confirm_sale(
        db=db,
        listing_id=listing_id,
        seller_roll=current_user.roll_no,
        is_admin=is_admin,
    )


@router.post("/{listing_id}/cancel-sale", response_model=ListingResponse)
def cancel_sale(
    listing_id: int,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    is_admin = bool(current_user.auth_account and current_user.auth_account.role == "ADMIN")
    return marketplace_service.cancel_sale(
        db=db,
        listing_id=listing_id,
        user_roll=current_user.roll_no,
        is_admin=is_admin,
    )
