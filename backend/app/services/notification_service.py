import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: uuid.UUID,
    notification_type: str,
    title: str,
    message: str,
    reservation_id: uuid.UUID | None = None
) -> Notification:

    notification = Notification(
        user_id=user_id,
        reservation_id=reservation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=False
    )

    db.add(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id: uuid.UUID
) -> list[Notification]:

    statement = (
        select(Notification)
        .where(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_unread_count(
    db: Session,
    user_id: uuid.UUID
) -> int:

    statement = select(
        func.count(Notification.id)
    ).where(
        Notification.user_id == user_id,
        Notification.is_read.is_(False)
    )

    return int(
        db.scalar(statement) or 0
    )


def mark_notification_read(
    db: Session,
    user_id: uuid.UUID,
    notification_id: uuid.UUID
) -> Notification | None:

    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id
    )

    notification = db.scalar(statement)

    if notification is None:
        return None

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_read(
    db: Session,
    user_id: uuid.UUID
) -> int:

    statement = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read.is_(False)
    )

    notifications = list(
        db.scalars(statement).all()
    )

    read_time = datetime.now(
        timezone.utc
    )

    for notification in notifications:
        notification.is_read = True
        notification.read_at = read_time

    db.commit()

    return len(notifications)
