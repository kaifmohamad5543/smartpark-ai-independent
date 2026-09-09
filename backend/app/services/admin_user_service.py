import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_admin_users(
    db: Session
) -> list[User]:
    statement = (
        select(User)
        .order_by(
            User.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_admin_user_by_id(
    db: Session,
    user_id: uuid.UUID
) -> User | None:
    return db.get(
        User,
        user_id
    )


def set_admin_user_status(
    db: Session,
    target_user: User,
    current_admin: User,
    is_active: bool
) -> User:

    if (
        target_user.id == current_admin.id
        and not is_active
    ):
        raise ValueError(
            "You cannot deactivate your own administrator account."
        )

    target_user.is_active = is_active

    db.commit()
    db.refresh(target_user)

    return target_user
