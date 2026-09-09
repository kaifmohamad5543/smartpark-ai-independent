import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, exists, or_, select
from sqlalchemy.orm import Session

from app.ml.predictor_v2 import predictor_v2

from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate
from app.services.parking_service import (
    get_parking_availability,
    get_parking_location_by_id
)
from app.services.parking_session_service import (
    complete_parking_session,
    create_parking_session
)
from app.services.payment_service import create_checkout_payment
from app.services.wallet_service import debit_wallet_for_payment
from app.services.notification_service import create_notification
from app.services.pricing_service import (
    calculate_dynamic_hourly_rate,
    calculate_estimated_cost
)
from app.services.vehicle_service import get_user_vehicle_by_id
from app.utils.booking_code import generate_booking_code


ACTIVE_RESERVATION_STATUSES = [
    "confirmed",
    "checked_in"
]


LONDON_TIMEZONE = ZoneInfo("Europe/London")


def reservation_is_within_opening_hours(
    parking_location,
    reserved_from,
    reserved_until
) -> bool:
    if parking_location.is_24_hours:
        return True

    opening_time = parking_location.opening_time
    closing_time = parking_location.closing_time

    if opening_time is None or closing_time is None:
        return False

    local_start = reserved_from.astimezone(
        LONDON_TIMEZONE
    )
    local_end = reserved_until.astimezone(
        LONDON_TIMEZONE
    )

    if opening_time == closing_time:
        return False

    if opening_time < closing_time:
        if local_start.date() != local_end.date():
            return False

        return (
            local_start.time().replace(
                tzinfo=None
            ) >= opening_time
            and local_end.time().replace(
                tzinfo=None
            ) <= closing_time
        )

    # Overnight opening period, for example
    # 20:00 until 06:00 the following morning.
    start_time = local_start.time().replace(
        tzinfo=None
    )

    if start_time >= opening_time:
        window_start = datetime.combine(
            local_start.date(),
            opening_time,
            tzinfo=LONDON_TIMEZONE,
        )

        window_end = datetime.combine(
            local_start.date() + timedelta(days=1),
            closing_time,
            tzinfo=LONDON_TIMEZONE,
        )

    elif start_time <= closing_time:
        window_start = datetime.combine(
            local_start.date() - timedelta(days=1),
            opening_time,
            tzinfo=LONDON_TIMEZONE,
        )

        window_end = datetime.combine(
            local_start.date(),
            closing_time,
            tzinfo=LONDON_TIMEZONE,
        )

    else:
        return False

    return (
        local_start >= window_start
        and local_end <= window_end
    )


def generate_unique_booking_code(
    db: Session
) -> str:
    for _ in range(20):
        booking_code = generate_booking_code()

        existing = db.scalar(
            select(Reservation).where(
                Reservation.booking_code == booking_code
            )
        )

        if not existing:
            return booking_code

    raise RuntimeError(
        "Unable to generate a unique booking code."
    )


def find_available_space(
    db: Session,
    parking_location_id: uuid.UUID,
    reserved_from,
    reserved_until
) -> ParkingSpace | None:

    now = datetime.now(timezone.utc)

    overlapping_reservation = exists().where(
        Reservation.parking_space_id == ParkingSpace.id,
        or_(
            and_(
                Reservation.status == "confirmed",
                Reservation.reserved_from < reserved_until,
                Reservation.reserved_until > reserved_from,
            ),
            and_(
                Reservation.status == "checked_in",
                Reservation.reserved_from < reserved_until,
            ),
        ),
    )

    conditions = [
        ParkingSpace.parking_location_id
        == parking_location_id,
        ParkingSpace.is_active == True,
        ~overlapping_reservation,
    ]

    # Current physical occupancy should only block a
    # reservation whose requested window includes now.
    # Future bookings are governed by scheduled conflicts.
    if reserved_from <= now < reserved_until:
        conditions.append(
            ParkingSpace.is_available == True
        )

    statement = (
        select(ParkingSpace)
        .where(*conditions)
        .order_by(
            ParkingSpace.space_number
        )
        .limit(1)
        .with_for_update(
            skip_locked=True
        )
    )

    return db.scalar(statement)


def create_reservation(
    db: Session,
    user_id: uuid.UUID,
    reservation_data: ReservationCreate
) -> Reservation:

    vehicle = get_user_vehicle_by_id(
        db=db,
        user_id=user_id,
        vehicle_id=reservation_data.vehicle_id
    )

    if not vehicle:
        raise ValueError(
            "Vehicle does not belong to the current user."
        )

    parking_location = get_parking_location_by_id(
        db=db,
        parking_location_id=(
            reservation_data.parking_location_id
        )
    )

    if not parking_location:
        raise ValueError(
            "Parking location not found."
        )

    if not reservation_is_within_opening_hours(
        parking_location=parking_location,
        reserved_from=reservation_data.reserved_from,
        reserved_until=reservation_data.reserved_until,
    ):
        raise ValueError(
            "The selected reservation time "
            "is outside this parking location's "
            "opening hours."
        )

    parking_space = find_available_space(
        db=db,
        parking_location_id=(
            reservation_data.parking_location_id
        ),
        reserved_from=reservation_data.reserved_from,
        reserved_until=reservation_data.reserved_until
    )

    if not parking_space:
        raise ValueError(
            "No parking space is available for the selected time."
        )

    availability = get_parking_availability(
        db=db,
        parking_location=parking_location
    )

    current_occupancy = availability[
        "occupancy_percentage"
    ]

    base_hourly_rate = (
        parking_location.hourly_rate
    )

    applied_hourly_rate = (
        parking_location.hourly_rate
    )

    pricing_multiplier = 1

    current_occupancy_at_booking = (
        current_occupancy
    )

    predicted_occupancy_at_booking = None

    pricing_model_version = "fixed-v1"

    if parking_location.dynamic_pricing_enabled:
        local_start = (
            reservation_data.reserved_from
            .astimezone(
                LONDON_TIMEZONE
            )
        )

        predicted_occupancy = (
            predictor_v2.predict(
                hour=local_start.hour,
                day_of_week=(
                    local_start.weekday()
                ),
                previous_occupancy=(
                    current_occupancy
                ),
                current_occupancy=(
                    current_occupancy
                ),

                # The reservation endpoint does
                # not currently consume external
                # live traffic/weather/event feeds.
                # Zero is therefore used as the
                # documented baseline input.
                traffic_level=0,
                weather=0,
                event_level=0,

                parking_price=float(
                    parking_location.hourly_rate
                ),
                total_spaces=availability[
                    "total_spaces"
                ],
            )
        )

        pricing = (
            calculate_dynamic_hourly_rate(
                base_hourly_rate=(
                    parking_location.hourly_rate
                ),
                reserved_from=(
                    reservation_data.reserved_from
                ),
                current_occupancy=(
                    current_occupancy
                ),
                predicted_occupancy=(
                    predicted_occupancy
                ),
            )
        )

        base_hourly_rate = pricing[
            "base_hourly_rate"
        ]

        applied_hourly_rate = pricing[
            "applied_hourly_rate"
        ]

        pricing_multiplier = pricing[
            "pricing_multiplier"
        ]

        current_occupancy_at_booking = (
            pricing[
                "current_occupancy"
            ]
        )

        predicted_occupancy_at_booking = (
            pricing[
                "predicted_occupancy"
            ]
        )

        pricing_model_version = (
            predictor_v2.model_version
        )

    estimated_cost = calculate_estimated_cost(
        reserved_from=(
            reservation_data.reserved_from
        ),
        reserved_until=(
            reservation_data.reserved_until
        ),
        hourly_rate=applied_hourly_rate
    )

    reservation = Reservation(
        user_id=user_id,
        vehicle_id=reservation_data.vehicle_id,
        parking_location_id=(
            reservation_data.parking_location_id
        ),
        parking_space_id=parking_space.id,
        booking_code=generate_unique_booking_code(db),
        reserved_from=reservation_data.reserved_from,
        reserved_until=reservation_data.reserved_until,
        status="confirmed",
        estimated_cost=estimated_cost,
        base_hourly_rate=base_hourly_rate,
        applied_hourly_rate=applied_hourly_rate,
        pricing_multiplier=pricing_multiplier,
        current_occupancy_at_booking=(
            current_occupancy_at_booking
        ),
        predicted_occupancy_at_booking=(
            predicted_occupancy_at_booking
        ),
        pricing_model_version=(
            pricing_model_version
        )
    )

    db.add(reservation)

    # Flush first so the reservation UUID is available
    # before creating the related notification.
    db.flush()

    create_notification(
        db=db,
        user_id=user_id,
        reservation_id=reservation.id,
        notification_type="reservation_confirmed",
        title="Reservation Confirmed",
        message=(
            f"Your reservation {reservation.booking_code} "
            f"at {parking_location.name} has been confirmed."
        )
    )

    db.commit()
    db.refresh(reservation)

    return reservation


def get_user_reservations(
    db: Session,
    user_id: uuid.UUID
) -> list[Reservation]:
    statement = (
        select(Reservation)
        .where(
            Reservation.user_id == user_id
        )
        .order_by(
            Reservation.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )



def get_user_reservation_by_id(
    db: Session,
    user_id: uuid.UUID,
    reservation_id: uuid.UUID
) -> Reservation | None:
    statement = select(Reservation).where(
        Reservation.id == reservation_id,
        Reservation.user_id == user_id
    )

    return db.scalar(statement)


def cancel_reservation(
    db: Session,
    reservation: Reservation
) -> Reservation:
    if reservation.status == "cancelled":
        raise ValueError(
            "Reservation has already been cancelled."
        )

    if reservation.status == "checked_in":
        raise ValueError(
            "A checked-in reservation cannot be cancelled."
        )

    if reservation.status == "completed":
        raise ValueError(
            "A completed reservation cannot be cancelled."
        )

    reservation.status = "cancelled"
    reservation.cancelled_at = datetime.now(timezone.utc)

    create_notification(
        db=db,
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        notification_type="reservation_cancelled",
        title="Reservation Cancelled",
        message=(
            f"Reservation {reservation.booking_code} "
            f"has been cancelled successfully."
        )
    )

    db.commit()
    db.refresh(reservation)

    return reservation


def get_user_reservation_by_booking_code(
    db: Session,
    user_id: uuid.UUID,
    booking_code: str
) -> Reservation | None:
    statement = select(Reservation).where(
        Reservation.user_id == user_id,
        Reservation.booking_code == booking_code.upper().strip()
    )

    return db.scalar(statement)


def check_in_reservation(
    db: Session,
    reservation: Reservation
) -> Reservation:
    if reservation.status == "cancelled":
        raise ValueError(
            "Cancelled reservations cannot be checked in."
        )

    if reservation.status == "completed":
        raise ValueError(
            "This reservation has already been completed."
        )

    if reservation.status == "checked_in":
        raise ValueError(
            "This reservation is already checked in."
        )

    now = datetime.now(timezone.utc)

    earliest_check_in = (
        reservation.reserved_from
        - timedelta(minutes=15)
    )

    if now < earliest_check_in:
        raise ValueError(
            "Check-in is only allowed from "
            "15 minutes before the reservation starts."
        )

    if now >= reservation.reserved_until:
        raise ValueError(
            "This reservation has expired "
            "and can no longer be checked in."
        )

    parking_space = db.get(
        ParkingSpace,
        reservation.parking_space_id
    )

    if not parking_space:
        raise ValueError(
            "Allocated parking space was not found."
        )

    reservation.status = "checked_in"
    reservation.checked_in_at = datetime.now(timezone.utc)

    parking_space.is_available = False

    if (
        parking_space.has_ev_charging
        and parking_space.ev_charger_status
        == "available"
    ):
        parking_space.ev_charger_status = (
            "occupied"
        )
        parking_space.ev_charger_updated_at = (
            datetime.now(timezone.utc)
        )

    create_parking_session(
        db=db,
        reservation=reservation
    )

    create_notification(
        db=db,
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        notification_type="check_in",
        title="Check-In Successful",
        message=(
            f"You have successfully checked in "
            f"for reservation {reservation.booking_code}."
        )
    )

    db.commit()
    db.refresh(reservation)

    return reservation


def check_out_reservation(
    db: Session,
    reservation: Reservation,
    payment_method: str = "card"
) -> Reservation:
    if reservation.status != "checked_in":
        raise ValueError(
            "Only a checked-in reservation can be checked out."
        )

    if not reservation.checked_in_at:
        raise ValueError(
            "Check-in time is missing."
        )

    parking_space = db.get(
        ParkingSpace,
        reservation.parking_space_id
    )

    if not parking_space:
        raise ValueError(
            "Allocated parking space was not found."
        )

    parking_location = get_parking_location_by_id(
        db=db,
        parking_location_id=reservation.parking_location_id
    )

    if not parking_location:
        raise ValueError(
            "Parking location was not found."
        )

    checked_out_at = datetime.now(timezone.utc)

    # Use the hourly rate that was locked
    # when the reservation was created.
    #
    # Legacy reservations created before
    # dynamic-pricing support may have NULL
    # snapshot fields, so they safely fall
    # back to the location rate.
    locked_hourly_rate = (
        reservation.applied_hourly_rate
        if reservation.applied_hourly_rate
        is not None
        else parking_location.hourly_rate
    )

    final_cost = calculate_estimated_cost(
        reserved_from=(
            reservation.checked_in_at
        ),
        reserved_until=checked_out_at,
        hourly_rate=locked_hourly_rate
    )

    reservation.checked_out_at = checked_out_at
    reservation.status = "completed"
    reservation.final_cost = final_cost

    parking_space.is_available = True

    if (
        parking_space.has_ev_charging
        and parking_space.ev_charger_status
        == "occupied"
    ):
        parking_space.ev_charger_status = (
            "available"
        )
        parking_space.ev_charger_updated_at = (
            datetime.now(timezone.utc)
        )

    parking_session = complete_parking_session(
        db=db,
        reservation=reservation,
        ended_at=checked_out_at,
        final_cost=final_cost
    )

    payment = create_checkout_payment(
        db=db,
        reservation=reservation,
        parking_session=parking_session,
        amount=final_cost,
        payment_method=payment_method
    )

    if payment_method == "wallet":
        debit_wallet_for_payment(
            db=db,
            user_id=reservation.user_id,
            amount=final_cost,
            reservation_id=reservation.id,
            payment_id=payment.id
        )

    create_notification(
        db=db,
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        notification_type="check_out",
        title="Check-Out Completed",
        message=(
            f"Reservation {reservation.booking_code} "
            f"has been completed. "
            f"Final parking cost: £{final_cost:.2f}."
        )
    )

    db.commit()
    db.refresh(reservation)

    return reservation
