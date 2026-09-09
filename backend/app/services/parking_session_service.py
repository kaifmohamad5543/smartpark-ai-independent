import math
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parking_session import ParkingSession
from app.models.reservation import Reservation


def get_session_by_reservation(
    db: Session,
    reservation_id: uuid.UUID
) -> ParkingSession | None:

    return db.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id == reservation_id
        )
    )


def create_parking_session(
    db: Session,
    reservation: Reservation
) -> ParkingSession:

    existing = get_session_by_reservation(
        db=db,
        reservation_id=reservation.id
    )

    if existing:
        return existing

    session = ParkingSession(
        reservation_id=reservation.id,
        user_id=reservation.user_id,
        parking_location_id=reservation.parking_location_id,
        parking_space_id=reservation.parking_space_id,
        started_at=reservation.checked_in_at,
        status="active"
    )

    db.add(session)
    db.flush()

    return session


def complete_parking_session(
    db: Session,
    reservation: Reservation,
    ended_at: datetime,
    final_cost: Decimal
) -> ParkingSession:

    session = get_session_by_reservation(
        db=db,
        reservation_id=reservation.id
    )

    if not session:
        raise ValueError(
            "Parking session was not found for this reservation."
        )

    elapsed_seconds = max(
        0,
        (
            ended_at - session.started_at
        ).total_seconds()
    )

    duration_minutes = (
        max(
            1,
            math.ceil(elapsed_seconds / 60)
        )
        if elapsed_seconds > 0
        else 0
    )

    session.ended_at = ended_at
    session.duration_minutes = duration_minutes
    session.final_cost = final_cost
    session.status = "completed"

    db.flush()

    return session


from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace


def get_user_parking_history(
    db: Session,
    user_id: uuid.UUID
) -> list[dict]:

    statement = (
        select(
            ParkingSession,
            Reservation.booking_code,
            ParkingLocation.name,
            ParkingSpace.space_number
        )
        .join(
            Reservation,
            Reservation.id
            == ParkingSession.reservation_id
        )
        .join(
            ParkingLocation,
            ParkingLocation.id
            == ParkingSession.parking_location_id
        )
        .join(
            ParkingSpace,
            ParkingSpace.id
            == ParkingSession.parking_space_id
        )
        .where(
            ParkingSession.user_id == user_id
        )
        .order_by(
            ParkingSession.created_at.desc()
        )
    )

    rows = db.execute(statement).all()

    history = []

    for (
        parking_session,
        booking_code,
        parking_name,
        space_number
    ) in rows:

        history.append(
            {
                "id": parking_session.id,
                "reservation_id": parking_session.reservation_id,
                "booking_code": booking_code,

                "parking_location_id":
                    parking_session.parking_location_id,

                "parking_name": parking_name,

                "parking_space_id":
                    parking_session.parking_space_id,

                "space_number": space_number,

                "started_at": parking_session.started_at,
                "ended_at": parking_session.ended_at,

                "duration_minutes":
                    parking_session.duration_minutes,

                "final_cost": parking_session.final_cost,

                "status": parking_session.status,
                "created_at": parking_session.created_at
            }
        )

    return history
