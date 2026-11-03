from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_active_user
from app.models.student import Student
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.schemas.common import PageResponse
from app.services import inquiry_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PageResponse[NotificationResponse], summary="List notifications for authenticated user")
def get_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return inquiry_service.get_notifications(
        db=db,
        user_roll=current_user.roll_no,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )


@router.get("/unread-count", response_model=UnreadCountResponse, summary="Get count of unread notifications")
def get_unread_count(
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    count = inquiry_service.get_unread_notification_count(
        db=db,
        user_roll=current_user.roll_no,
    )
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Mark a notification as read")
def mark_as_read(
    notification_id: int,
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return inquiry_service.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_roll=current_user.roll_no,
    )


@router.patch("/read-all", summary="Mark all notifications as read for current user")
def mark_all_as_read(
    current_user: Student = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updated = inquiry_service.mark_all_notifications_as_read(
        db=db,
        user_roll=current_user.roll_no,
    )
    return {"message": f"{updated} notifications marked as read."}

