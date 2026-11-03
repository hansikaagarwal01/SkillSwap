from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_active_user
from app.models.student import Student
from app.schemas.inquiry import InquiryCreate, InquiryStatusUpdate, InquiryResponse
from app.schemas.common import PageResponse
from app.services import inquiry_service

router = APIRouter(tags=["Marketplace Inquiries"])


@router.post(
    "/marketplace/listings/{listing_id}/inquiries",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an inquiry to the seller regarding a listing",
)
def create_inquiry(
    listing_id: int,
    payload: InquiryCreate,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return inquiry_service.create_inquiry(
        db=db,
        listing_id=listing_id,
        buyer=current_user,
        data=payload,
    )


@router.get(
    "/marketplace/inquiries/received",
    response_model=PageResponse[InquiryResponse],
    summary="List all product inquiries received by the authenticated seller",
)
def get_received_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return inquiry_service.get_received_inquiries(
        db=db,
        seller_roll=current_user.roll_no,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/marketplace/inquiries/sent",
    response_model=PageResponse[InquiryResponse],
    summary="List all inquiries sent by the authenticated buyer",
)
def get_sent_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return inquiry_service.get_sent_inquiries(
        db=db,
        buyer_roll=current_user.roll_no,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/marketplace/inquiries/{inquiry_id}/status",
    response_model=InquiryResponse,
    summary="Update the status of an inquiry (seller or admin)",
)
def update_inquiry_status(
    inquiry_id: int,
    payload: InquiryStatusUpdate,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    is_admin = bool(current_user.auth_account and current_user.auth_account.role == "ADMIN")
    return inquiry_service.update_inquiry_status(
        db=db,
        inquiry_id=inquiry_id,
        new_status=payload.status,
        user_roll=current_user.roll_no,
        is_admin=is_admin,
    )

