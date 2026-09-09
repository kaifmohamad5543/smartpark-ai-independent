from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.parking_location import ParkingLocation
from app.models.parking_session import ParkingSession
from app.models.parking_space import ParkingSpace
from app.models.prediction import Prediction
from app.models.reservation import Reservation
from app.models.user import User
from app.models.payment import Payment


def count_reservations_by_status(
    db: Session,
    reservation_status: str
) -> int:
    return int(
        db.scalar(
            select(
                func.count(Reservation.id)
            ).where(
                Reservation.status == reservation_status
            )
        )
        or 0
    )


def get_admin_analytics_overview(
    db: Session
) -> dict:

    total_users = int(
        db.scalar(
            select(func.count(User.id))
        )
        or 0
    )

    active_users = int(
        db.scalar(
            select(func.count(User.id)).where(
                User.is_active.is_(True)
            )
        )
        or 0
    )

    total_reservations = int(
        db.scalar(
            select(func.count(Reservation.id))
        )
        or 0
    )

    completed_parking_sessions = int(
        db.scalar(
            select(
                func.count(ParkingSession.id)
            ).where(
                ParkingSession.status == "completed"
            )
        )
        or 0
    )

    gross_payment_revenue = float(
        db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    0
                )
            ).where(
                Payment.transaction_type == "parking_charge"
            )
        )
        or 0
    )

    total_refunds = float(
        db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    0
                )
            ).where(
                Payment.transaction_type == "refund"
            )
        )
        or 0
    )

    total_revenue = (
        gross_payment_revenue
        - total_refunds
    )

    total_parking_locations = int(
        db.scalar(
            select(
                func.count(ParkingLocation.id)
            ).where(
                ParkingLocation.is_active.is_(True)
            )
        )
        or 0
    )

    total_parking_spaces = int(
        db.scalar(
            select(
                func.count(ParkingSpace.id)
            )
            .join(
                ParkingLocation,
                ParkingSpace.parking_location_id
                == ParkingLocation.id
            )
            .where(
                ParkingSpace.is_active.is_(True),
                ParkingLocation.is_active.is_(True)
            )
        )
        or 0
    )

    available_parking_spaces = int(
        db.scalar(
            select(
                func.count(ParkingSpace.id)
            )
            .join(
                ParkingLocation,
                ParkingSpace.parking_location_id
                == ParkingLocation.id
            )
            .where(
                ParkingSpace.is_active.is_(True),
                ParkingSpace.is_available.is_(True),
                ParkingLocation.is_active.is_(True)
            )
        )
        or 0
    )

    if total_parking_spaces > 0:
        occupied_spaces = (
            total_parking_spaces
            - available_parking_spaces
        )

        overall_occupancy_percentage = round(
            (
                occupied_spaces
                / total_parking_spaces
            )
            * 100,
            2
        )
    else:
        overall_occupancy_percentage = 0.0

    total_predictions = int(
        db.scalar(
            select(
                func.count(Prediction.id)
            )
        )
        or 0
    )

    average_predicted_occupancy = float(
        db.scalar(
            select(
                func.avg(
                    Prediction.predicted_occupancy
                )
            )
        )
        or 0
    )

    return {
        "total_users": total_users,
        "active_users": active_users,

        "total_reservations": total_reservations,

        "confirmed_reservations":
            count_reservations_by_status(
                db,
                "confirmed"
            ),

        "checked_in_reservations":
            count_reservations_by_status(
                db,
                "checked_in"
            ),

        "cancelled_reservations":
            count_reservations_by_status(
                db,
                "cancelled"
            ),

        "completed_reservations":
            count_reservations_by_status(
                db,
                "completed"
            ),

        "completed_parking_sessions":
            completed_parking_sessions,

        "total_revenue":
            round(total_revenue, 2),

        "total_parking_locations":
            total_parking_locations,

        "total_parking_spaces":
            total_parking_spaces,

        "available_parking_spaces":
            available_parking_spaces,

        "overall_occupancy_percentage":
            overall_occupancy_percentage,

        "total_predictions":
            total_predictions,

        "average_predicted_occupancy":
            round(
                average_predicted_occupancy,
                2
            )
    }


from app.models.review import Review


def get_parking_location_performance(
    db: Session
) -> list[dict]:

    locations = list(
        db.scalars(
            select(ParkingLocation)
            .where(
                ParkingLocation.is_active.is_(True)
            )
            .order_by(ParkingLocation.name)
        ).all()
    )

    results = []

    for location in locations:

        total_spaces = int(
            db.scalar(
                select(
                    func.count(ParkingSpace.id)
                ).where(
                    ParkingSpace.parking_location_id
                    == location.id,
                    ParkingSpace.is_active.is_(True)
                )
            )
            or 0
        )

        available_spaces = int(
            db.scalar(
                select(
                    func.count(ParkingSpace.id)
                ).where(
                    ParkingSpace.parking_location_id
                    == location.id,
                    ParkingSpace.is_active.is_(True),
                    ParkingSpace.is_available.is_(True)
                )
            )
            or 0
        )

        if total_spaces > 0:
            current_occupancy = round(
                (
                    (
                        total_spaces
                        - available_spaces
                    )
                    / total_spaces
                )
                * 100,
                2
            )
        else:
            current_occupancy = 0.0

        total_reservations = int(
            db.scalar(
                select(
                    func.count(Reservation.id)
                ).where(
                    Reservation.parking_location_id
                    == location.id
                )
            )
            or 0
        )

        completed_reservations = int(
            db.scalar(
                select(
                    func.count(Reservation.id)
                ).where(
                    Reservation.parking_location_id
                    == location.id,
                    Reservation.status == "completed"
                )
            )
            or 0
        )

        cancelled_reservations = int(
            db.scalar(
                select(
                    func.count(Reservation.id)
                ).where(
                    Reservation.parking_location_id
                    == location.id,
                    Reservation.status == "cancelled"
                )
            )
            or 0
        )

        completed_sessions = int(
            db.scalar(
                select(
                    func.count(ParkingSession.id)
                ).where(
                    ParkingSession.parking_location_id
                    == location.id,
                    ParkingSession.status == "completed"
                )
            )
            or 0
        )

        gross_location_revenue = float(
            db.scalar(
                select(
                    func.coalesce(
                        func.sum(Payment.amount),
                        0
                    )
                )
                .join(
                    Reservation,
                    Payment.reservation_id
                    == Reservation.id
                )
                .where(
                    Reservation.parking_location_id
                    == location.id,
                    Payment.transaction_type
                    == "parking_charge"
                )
            )
            or 0
        )

        location_refunds = float(
            db.scalar(
                select(
                    func.coalesce(
                        func.sum(Payment.amount),
                        0
                    )
                )
                .join(
                    Reservation,
                    Payment.reservation_id
                    == Reservation.id
                )
                .where(
                    Reservation.parking_location_id
                    == location.id,
                    Payment.transaction_type
                    == "refund"
                )
            )
            or 0
        )

        total_revenue = (
            gross_location_revenue
            - location_refunds
        )

        average_prediction = float(
            db.scalar(
                select(
                    func.avg(
                        Prediction.predicted_occupancy
                    )
                ).where(
                    Prediction.parking_location_id
                    == location.id
                )
            )
            or 0
        )

        rating_result = db.execute(
            select(
                func.avg(Review.rating),
                func.count(Review.id)
            ).where(
                Review.parking_location_id
                == location.id
            )
        ).one()

        average_rating = (
            float(rating_result[0])
            if rating_result[0] is not None
            else 0.0
        )

        review_count = int(
            rating_result[1]
        )

        results.append(
            {
                "parking_location_id":
                    str(location.id),

                "parking_name":
                    location.name,

                "total_spaces":
                    total_spaces,

                "available_spaces":
                    available_spaces,

                "current_occupancy_percentage":
                    current_occupancy,

                "total_reservations":
                    total_reservations,

                "completed_reservations":
                    completed_reservations,

                "cancelled_reservations":
                    cancelled_reservations,

                "completed_sessions":
                    completed_sessions,

                "total_revenue":
                    round(total_revenue, 2),

                "average_predicted_occupancy":
                    round(
                        average_prediction,
                        2
                    ),

                "average_rating":
                    round(
                        average_rating,
                        2
                    ),

                "review_count":
                    review_count
            }
        )

    return results


from datetime import datetime, timedelta, timezone


def get_reservation_trends(
    db: Session,
    days: int = 7
) -> list[dict]:

    start_date = (
        datetime.now(timezone.utc)
        - timedelta(days=days - 1)
    ).date()

    rows = db.execute(
        select(
            func.date(
                func.timezone(
                    "UTC",
                    Reservation.created_at
                )
            ).label("reservation_date"),

            Reservation.status,

            func.count(
                Reservation.id
            ).label("reservation_count")
        )
        .where(
            func.date(
                func.timezone(
                    "UTC",
                    Reservation.created_at
                )
            ) >= start_date
        )
        .group_by(
            func.date(
                func.timezone(
                    "UTC",
                    Reservation.created_at
                )
            ),
            Reservation.status
        )
        .order_by(
            func.date(
                func.timezone(
                    "UTC",
                    Reservation.created_at
                )
            )
        )
    ).all()

    grouped = {}

    for (
        reservation_date,
        reservation_status,
        reservation_count
    ) in rows:

        # SQLite returns func.date(...) as a string,
        # while PostgreSQL may return a date object.
        # Normalise both forms before grouping.
        if isinstance(reservation_date, str):
            reservation_date = (
                datetime.fromisoformat(
                    reservation_date
                ).date()
            )

        if reservation_date not in grouped:
            grouped[reservation_date] = {
                "date": reservation_date,
                "total_reservations": 0,
                "confirmed": 0,
                "checked_in": 0,
                "completed": 0,
                "cancelled": 0
            }

        count = int(
            reservation_count
        )

        grouped[
            reservation_date
        ]["total_reservations"] += count

        if reservation_status in {
            "confirmed",
            "checked_in",
            "completed",
            "cancelled"
        }:
            grouped[
                reservation_date
            ][reservation_status] += count

    results = []

    for offset in range(days):
        current_date = (
            start_date
            + timedelta(days=offset)
        )

        results.append(
            grouped.get(
                current_date,
                {
                    "date": current_date,
                    "total_reservations": 0,
                    "confirmed": 0,
                    "checked_in": 0,
                    "completed": 0,
                    "cancelled": 0
                }
            )
        )

    return results


def classify_demand(
    predicted_occupancy: float
) -> str:
    if predicted_occupancy < 40:
        return "LOW"

    if predicted_occupancy < 70:
        return "MEDIUM"

    if predicted_occupancy < 85:
        return "HIGH"

    return "VERY HIGH"


def get_ai_demand_analytics(
    db: Session,
    limit: int = 20
) -> dict:

    rows = db.execute(
        select(
            Prediction,
            ParkingLocation.name
        )
        .join(
            ParkingLocation,
            ParkingLocation.id
            == Prediction.parking_location_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .limit(limit)
    ).all()

    all_predictions = list(
        db.scalars(
            select(Prediction)
        ).all()
    )

    demand_counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "VERY HIGH": 0
    }

    occupancy_values = []

    for prediction in all_predictions:
        occupancy = float(
            prediction.predicted_occupancy
        )

        occupancy_values.append(
            occupancy
        )

        level = classify_demand(
            occupancy
        )

        demand_counts[level] += 1

    if occupancy_values:
        average_occupancy = round(
            sum(occupancy_values)
            / len(occupancy_values),
            2
        )
    else:
        average_occupancy = 0.0

    recent_predictions = []

    for prediction, parking_name in rows:
        occupancy = float(
            prediction.predicted_occupancy
        )

        recent_predictions.append(
            {
                "prediction_id":
                    str(prediction.id),

                "parking_location_id":
                    str(
                        prediction.parking_location_id
                    ),

                "parking_name":
                    parking_name,

                "predicted_occupancy":
                    round(occupancy, 2),

                "predicted_availability":
                    round(
                        float(
                            prediction.predicted_availability
                        ),
                        2
                    ),

                "demand_level":
                    classify_demand(
                        occupancy
                    ),

                "created_at":
                    prediction.created_at
            }
        )

    return {
        "total_predictions":
            len(all_predictions),

        "average_predicted_occupancy":
            average_occupancy,

        "low_demand_count":
            demand_counts["LOW"],

        "medium_demand_count":
            demand_counts["MEDIUM"],

        "high_demand_count":
            demand_counts["HIGH"],

        "very_high_demand_count":
            demand_counts["VERY HIGH"],

        "recent_predictions":
            recent_predictions
    }
