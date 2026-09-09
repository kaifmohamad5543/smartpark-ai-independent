import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.review import Review
from app.schemas.review import ReviewCreate


def get_user_review_for_location(
    db: Session,
    user_id: uuid.UUID,
    parking_location_id: uuid.UUID
) -> Review | None:

    statement = select(Review).where(
        Review.user_id == user_id,
        Review.parking_location_id == parking_location_id
    )

    return db.scalar(statement)


def create_review(
    db: Session,
    user_id: uuid.UUID,
    review_data: ReviewCreate
) -> Review:

    existing_review = get_user_review_for_location(
        db=db,
        user_id=user_id,
        parking_location_id=review_data.parking_location_id
    )

    if existing_review:
        raise ValueError(
            "You have already reviewed this parking location."
        )

    review = Review(
        user_id=user_id,
        parking_location_id=review_data.parking_location_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_reviews_for_location(
    db: Session,
    parking_location_id: uuid.UUID
) -> list[Review]:

    statement = (
        select(Review)
        .where(
            Review.parking_location_id == parking_location_id
        )
        .order_by(
            Review.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_average_rating(
    db: Session,
    parking_location_id: uuid.UUID
) -> tuple[float, int]:

    result = db.execute(
        select(
            func.avg(Review.rating),
            func.count(Review.id)
        ).where(
            Review.parking_location_id == parking_location_id
        )
    ).one()

    average_rating = (
        float(result[0])
        if result[0] is not None
        else 0.0
    )

    review_count = int(
        result[1]
    )

    return (
        round(average_rating, 2),
        review_count
    )
