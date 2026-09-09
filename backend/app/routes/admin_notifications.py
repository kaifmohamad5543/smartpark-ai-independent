from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_notification import (
    AdminNotificationResponse,
    AdminNotificationSendRequest,
    AdminNotificationSendResponse,
)
from app.services.admin_notification_service import (
    get_admin_notifications,
    send_admin_notification,
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/notifications",
    tags=["Admin Notification Management"],
)


@router.get(
    "",
    response_model=list[AdminNotificationResponse],
)
def list_admin_notifications(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return get_admin_notifications(
        db=db
    )


@router.post(
    "/send",
    response_model=AdminNotificationSendResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_notification_from_admin(
    notification_data: AdminNotificationSendRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    try:
        created_count = (
            send_admin_notification(
                db=db,
                notification_data=notification_data,
            )
        )

        return AdminNotificationSendResponse(
            created_count=created_count,
            message=(
                f"Notification sent successfully "
                f"to {created_count} user"
                f"{'' if created_count == 1 else 's'}."
            ),
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
