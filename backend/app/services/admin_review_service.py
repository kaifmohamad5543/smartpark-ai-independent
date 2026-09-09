import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parking_location import ParkingLocation
from app.models.review import Review
from app.models.user import User


def get_admin_reviews(
    db: Session
) -> list[dict]:

    statement = (
        select(
            Review,
            User.full_name,
            User.email,
            ParkingLocation.name,
        )
        .join(
            User,
            User.id == Review.user_id
        )
        .join(
            ParkingLocation,
            ParkingLocation.id
            == Review.parking_location_id
        )
        .order_by(
            Review.created_at.desc()
        )
    )

    rows = db.execute(
        statement
    ).all()

    results = []

    for (
        review,
        user_name,
        user_email,
        parking_location_name,
    ) in rows:

        results.append(
            {
                "id": review.id,

                "user_id": review.user_id,
                "user_name": user_name,
                "user_email": user_email,

                "parking_location_id": (
                    review.parking_location_id
                ),
                "parking_location_name": (
                    parking_location_name
                ),

                "rating": review.rating,
                "comment": review.comment,

                "created_at": review.created_at,
                "updated_at": review.updated_at,
            }
        )

    return results


def get_admin_review_by_id(
    db: Session,
    review_id: uuid.UUID
) -> Review | None:

    return db.get(
        Review,
        review_id
    )


def delete_admin_review(
    db: Session,
    review: Review
) -> uuid.UUID:

    review_id = review.id

    db.delete(review)
    db.commit()

    return review_id
