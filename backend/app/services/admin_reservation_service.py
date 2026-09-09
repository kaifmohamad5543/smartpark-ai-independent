import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle


def get_admin_reservations(
    db: Session
) -> list[dict]:

    statement = (
        select(
            Reservation,
            User.full_name,
            User.email,
            Vehicle.registration_number,
            Vehicle.make,
            Vehicle.model,
            ParkingLocation.name,
            ParkingSpace.space_number,
            ParkingSpace.space_type,
        )
        .join(
            User,
            User.id == Reservation.user_id
        )
        .join(
            Vehicle,
            Vehicle.id == Reservation.vehicle_id
        )
        .join(
            ParkingLocation,
            ParkingLocation.id
            == Reservation.parking_location_id
        )
        .join(
            ParkingSpace,
            ParkingSpace.id
            == Reservation.parking_space_id
        )
        .order_by(
            Reservation.created_at.desc()
        )
    )

    rows = db.execute(
        statement
    ).all()

    results = []

    for (
        reservation,
        user_name,
        user_email,
        vehicle_registration,
        vehicle_make,
        vehicle_model,
        parking_location_name,
        parking_space_number,
        parking_space_type,
    ) in rows:

        results.append(
            {
                "id": reservation.id,
                "booking_code": (
                    reservation.booking_code
                ),

                "user_id": (
                    reservation.user_id
                ),
                "user_name": user_name,
                "user_email": user_email,

                "vehicle_id": (
                    reservation.vehicle_id
                ),
                "vehicle_registration": (
                    vehicle_registration
                ),
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,

                "parking_location_id": (
                    reservation.parking_location_id
                ),
                "parking_location_name": (
                    parking_location_name
                ),

                "parking_space_id": (
                    reservation.parking_space_id
                ),
                "parking_space_number": (
                    parking_space_number
                ),
                "parking_space_type": (
                    parking_space_type
                ),

                "reserved_from": (
                    reservation.reserved_from
                ),
                "reserved_until": (
                    reservation.reserved_until
                ),

                "status": (
                    reservation.status
                ),

                "estimated_cost": (
                    reservation.estimated_cost
                ),
                "final_cost": (
                    reservation.final_cost
                ),

                "checked_in_at": (
                    reservation.checked_in_at
                ),
                "checked_out_at": (
                    reservation.checked_out_at
                ),
                "cancelled_at": (
                    reservation.cancelled_at
                ),

                "created_at": (
                    reservation.created_at
                ),
                "updated_at": (
                    reservation.updated_at
                ),
            }
        )

    return results


def get_admin_reservation_by_id(
    db: Session,
    reservation_id: uuid.UUID
) -> Reservation | None:

    return db.get(
        Reservation,
        reservation_id
    )
