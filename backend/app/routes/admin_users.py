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
from app.schemas.admin_user import (
    AdminUserResponse,
    AdminUserStatusUpdate
)
from app.services.admin_user_service import (
    get_admin_user_by_id,
    get_admin_users,
    set_admin_user_status
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/users",
    tags=["Admin User Management"]
)


@router.get(
    "",
    response_model=list[AdminUserResponse]
)
def list_admin_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_admin_users(
        db=db
    )


@router.patch(
    "/{user_id}/status",
    response_model=AdminUserResponse
)
def update_admin_user_status(
    user_id: uuid.UUID,
    status_data: AdminUserStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    target_user = get_admin_user_by_id(
        db=db,
        user_id=user_id
    )

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    try:
        return set_admin_user_status(
            db=db,
            target_user=target_user,
            current_admin=admin_user,
            is_active=status_data.is_active
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
