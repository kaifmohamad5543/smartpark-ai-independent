import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadNotificationCount
)
from app.services.notification_service import (
    get_unread_count,
    get_user_notifications,
    mark_all_notifications_read,
    mark_notification_read
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=list[NotificationResponse]
)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_notifications(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/unread-count",
    response_model=UnreadNotificationCount
)
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = get_unread_count(
        db=db,
        user_id=current_user.id
    )

    return UnreadNotificationCount(
        unread_count=count
    )


@router.patch(
    "/read-all",
    response_model=MarkAllReadResponse
)
def read_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_count = mark_all_notifications_read(
        db=db,
        user_id=current_user.id
    )

    return MarkAllReadResponse(
        updated_count=updated_count,
        message="All notifications marked as read."
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def read_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = mark_notification_read(
        db=db,
        user_id=current_user.id,
        notification_id=notification_id
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )

    return notification
