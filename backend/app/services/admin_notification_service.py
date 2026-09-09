from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.admin_notification import (
    AdminNotificationSendRequest,
)
from app.services.notification_service import (
    create_notification,
)


def get_admin_notifications(
    db: Session,
) -> list[dict]:

    statement = (
        select(
            Notification,
            User.full_name,
            User.email,
            Reservation.booking_code,
        )
        .join(
            User,
            User.id == Notification.user_id,
        )
        .outerjoin(
            Reservation,
            Reservation.id
            == Notification.reservation_id,
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    rows = db.execute(
        statement
    ).all()

    results = []

    for (
        notification,
        user_name,
        user_email,
        booking_code,
    ) in rows:

        results.append(
            {
                "id": notification.id,

                "user_id": notification.user_id,
                "user_name": user_name,
                "user_email": user_email,

                "reservation_id": (
                    notification.reservation_id
                ),
                "booking_code": booking_code,

                "notification_type": (
                    notification.notification_type
                ),
                "title": notification.title,
                "message": notification.message,

                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
            }
        )

    return results


def send_admin_notification(
    db: Session,
    notification_data: AdminNotificationSendRequest,
) -> int:

    if (
        notification_data.recipient_mode
        == "all_active"
    ):
        users = list(
            db.scalars(
                select(User)
                .where(
                    User.is_active.is_(True)
                )
                .order_by(User.created_at)
            ).all()
        )

    else:
        target_user = db.get(
            User,
            notification_data.user_id,
        )

        if target_user is None:
            raise ValueError(
                "Selected user was not found."
            )

        if not target_user.is_active:
            raise ValueError(
                "Notifications can only be sent to an active user."
            )

        users = [
            target_user
        ]

    if not users:
        raise ValueError(
            "No active users were found."
        )

    for user in users:
        create_notification(
            db=db,
            user_id=user.id,
            notification_type="admin_announcement",
            title=notification_data.title.strip(),
            message=notification_data.message.strip(),
        )

    db.commit()

    return len(users)
