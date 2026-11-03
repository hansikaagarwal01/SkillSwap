from math import ceil
from typing import Optional, List
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.inquiry import MarketplaceInquiry
from app.models.notification import Notification
from app.models.listing import Listing
from app.models.student import Student
from app.schemas.inquiry import InquiryCreate, InquiryResponse
from app.schemas.notification import NotificationResponse
from app.schemas.common import PageResponse
from app.core.email import send_marketplace_inquiry_email


def _to_inquiry_response(inq: MarketplaceInquiry) -> InquiryResponse:
    return InquiryResponse(
        inquiry_id=inq.inquiry_id,
        listing_id=inq.listing_id,
        listing_title=inq.listing.title if inq.listing else "Listing",
        listing_price=inq.listing.price if inq.listing else 0.00,
        buyer_roll_no=inq.buyer_roll_no,
        buyer_name=inq.buyer.name if inq.buyer else inq.buyer_roll_no,
        buyer_email=inq.buyer.email if inq.buyer else f"{inq.buyer_roll_no.lower()}@jklu.edu.in",
        seller_roll_no=inq.seller_roll_no,
        seller_name=inq.seller.name if inq.seller else inq.seller_roll_no,
        seller_email=inq.seller.email if inq.seller else f"{inq.seller_roll_no.lower()}@jklu.edu.in",
        message=inq.message,
        inquiry_status=inq.inquiry_status,
        email_delivery_status=inq.email_delivery_status,
        email_delivery_error=inq.email_delivery_error,
        created_at=inq.created_at,
    )


def _to_notification_response(n: Notification) -> NotificationResponse:
    return NotificationResponse(
        notification_id=n.notification_id,
        recipient_roll_no=n.recipient_roll_no,
        inquiry_id=n.inquiry_id,
        title=n.title,
        message=n.message,
        is_read=n.is_read,
        created_at=n.created_at,
    )


def create_inquiry(
    db: Session,
    listing_id: int,
    buyer: Student,
    data: InquiryCreate,
) -> InquiryResponse:
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace listing not found",
        )

    if listing.status == "REMOVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot inquire about a removed listing",
        )

    if listing.seller_roll_no == buyer.roll_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send an inquiry for your own listing",
        )

    seller = db.query(Student).filter(Student.roll_no == listing.seller_roll_no).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller profile not found",
        )

    # Dispatch email notification using authentic stored emails
    _, delivery_status, delivery_error = send_marketplace_inquiry_email(
        seller_email=seller.email,
        seller_name=seller.name,
        buyer_name=buyer.name,
        buyer_roll_no=buyer.roll_no,
        buyer_email=buyer.email,
        product_title=listing.title,
        inquiry_message=data.message.strip(),
    )

    # Create MarketplaceInquiry record
    new_inquiry = MarketplaceInquiry(
        listing_id=listing.listing_id,
        buyer_roll_no=buyer.roll_no,
        seller_roll_no=listing.seller_roll_no,
        message=data.message.strip(),
        inquiry_status="PENDING",
        email_delivery_status=delivery_status,
        email_delivery_error=delivery_error,
    )
    db.add(new_inquiry)
    db.flush()

    # Create in-app Notification for the seller
    notification = Notification(
        recipient_roll_no=listing.seller_roll_no,
        inquiry_id=new_inquiry.inquiry_id,
        title="New Marketplace Inquiry",
        message=f"{buyer.name} ({buyer.roll_no}) is interested in '{listing.title}': {data.message.strip()}",
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(new_inquiry)

    return _to_inquiry_response(new_inquiry)


def get_received_inquiries(
    db: Session,
    seller_roll: str,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[InquiryResponse]:
    query = db.query(MarketplaceInquiry).filter(MarketplaceInquiry.seller_roll_no == seller_roll)
    total = query.count()
    items = (
        query.order_by(desc(MarketplaceInquiry.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    return PageResponse[InquiryResponse](
        items=[_to_inquiry_response(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_sent_inquiries(
    db: Session,
    buyer_roll: str,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[InquiryResponse]:
    query = db.query(MarketplaceInquiry).filter(MarketplaceInquiry.buyer_roll_no == buyer_roll)
    total = query.count()
    items = (
        query.order_by(desc(MarketplaceInquiry.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    return PageResponse[InquiryResponse](
        items=[_to_inquiry_response(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def update_inquiry_status(
    db: Session,
    inquiry_id: int,
    new_status: str,
    user_roll: str,
    is_admin: bool = False,
) -> InquiryResponse:
    inquiry = db.query(MarketplaceInquiry).filter(MarketplaceInquiry.inquiry_id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )

    if inquiry.seller_roll_no != user_roll and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the seller can update the inquiry status",
        )

    inquiry.inquiry_status = new_status
    db.commit()
    db.refresh(inquiry)
    return _to_inquiry_response(inquiry)


def get_notifications(
    db: Session,
    user_roll: str,
    unread_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> PageResponse[NotificationResponse]:
    query = db.query(Notification).filter(Notification.recipient_roll_no == user_roll)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    total = query.count()
    items = (
        query.order_by(desc(Notification.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = ceil(total / page_size) if total > 0 else 1
    return PageResponse[NotificationResponse](
        items=[_to_notification_response(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_unread_notification_count(db: Session, user_roll: str) -> int:
    return (
        db.query(func.count(Notification.notification_id))
        .filter(Notification.recipient_roll_no == user_roll, Notification.is_read.is_(False))
        .scalar()
        or 0
    )


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_roll: str,
) -> NotificationResponse:
    notification = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id, Notification.recipient_roll_no == user_roll)
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return _to_notification_response(notification)


def mark_all_notifications_as_read(db: Session, user_roll: str) -> int:
    updated = (
        db.query(Notification)
        .filter(Notification.recipient_roll_no == user_roll, Notification.is_read.is_(False))
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return updated

