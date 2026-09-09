import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.review import (
    ParkingRatingSummary,
    ReviewCreate,
    ReviewResponse
)
from app.services.review_service import (
    create_review,
    get_average_rating,
    get_reviews_for_location
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/reviews",
    tags=["Reviews"]
)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def add_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_review(
            db=db,
            user_id=current_user.id,
            review_data=review_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.get(
    "/location/{parking_location_id}",
    response_model=list[ReviewResponse]
)
def list_location_reviews(
    parking_location_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    return get_reviews_for_location(
        db=db,
        parking_location_id=parking_location_id
    )


@router.get(
    "/location/{parking_location_id}/summary",
    response_model=ParkingRatingSummary
)
def location_rating_summary(
    parking_location_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    average_rating, review_count = get_average_rating(
        db=db,
        parking_location_id=parking_location_id
    )

    return ParkingRatingSummary(
        parking_location_id=parking_location_id,
        average_rating=average_rating,
        review_count=review_count
    )
