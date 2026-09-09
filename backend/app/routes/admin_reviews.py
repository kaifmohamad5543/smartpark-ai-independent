import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_review import (
    AdminReviewDeleteResponse,
    AdminReviewResponse,
)
from app.services.admin_review_service import (
    delete_admin_review,
    get_admin_review_by_id,
    get_admin_reviews,
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/reviews",
    tags=["Admin Review Management"],
)


@router.get(
    "",
    response_model=list[AdminReviewResponse],
)
def list_admin_reviews(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return get_admin_reviews(
        db=db
    )


@router.delete(
    "/{review_id}",
    response_model=AdminReviewDeleteResponse,
)
def remove_admin_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    review = get_admin_review_by_id(
        db=db,
        review_id=review_id,
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    deleted_id = delete_admin_review(
        db=db,
        review=review,
    )

    return AdminReviewDeleteResponse(
        deleted_review_id=deleted_id,
        message="Review removed successfully.",
    )
