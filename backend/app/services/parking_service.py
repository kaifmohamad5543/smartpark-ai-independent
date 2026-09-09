import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace


def get_active_parking_locations(
    db: Session
) -> list[ParkingLocation]:
    statement = (
        select(ParkingLocation)
        .where(ParkingLocation.is_active == True)
        .order_by(ParkingLocation.name)
    )

    return list(db.scalars(statement).all())


def get_parking_location_by_id(
    db: Session,
    parking_location_id: uuid.UUID
) -> ParkingLocation | None:
    statement = select(ParkingLocation).where(
        ParkingLocation.id == parking_location_id,
        ParkingLocation.is_active == True
    )

    return db.scalar(statement)


def get_parking_availability(
    db: Session,
    parking_location: ParkingLocation
) -> dict:
    total_spaces = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id == parking_location.id,
            ParkingSpace.is_active == True
        )
    ) or 0

    available_spaces = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.is_available == True
        )
    ) or 0

    occupied_spaces = total_spaces - available_spaces

    occupancy_percentage = (
        round((occupied_spaces / total_spaces) * 100, 2)
        if total_spaces > 0
        else 0.0
    )

    total_ev_chargers = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id
            == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.has_ev_charging == True
        )
    ) or 0

    available_ev_chargers = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id
            == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.has_ev_charging == True,
            ParkingSpace.ev_charger_status
            == "available"
        )
    ) or 0

    occupied_ev_chargers = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id
            == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.has_ev_charging == True,
            ParkingSpace.ev_charger_status
            == "occupied"
        )
    ) or 0

    offline_ev_chargers = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id
            == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.has_ev_charging == True,
            ParkingSpace.ev_charger_status
            == "offline"
        )
    ) or 0

    maintenance_ev_chargers = db.scalar(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.parking_location_id
            == parking_location.id,
            ParkingSpace.is_active == True,
            ParkingSpace.has_ev_charging == True,
            ParkingSpace.ev_charger_status
            == "maintenance"
        )
    ) or 0

    return {
        "parking_location_id": parking_location.id,
        "parking_name": parking_location.name,
        "total_spaces": total_spaces,
        "available_spaces": available_spaces,
        "occupied_spaces": occupied_spaces,
        "occupancy_percentage": occupancy_percentage,
        "total_ev_chargers": total_ev_chargers,
        "available_ev_chargers": available_ev_chargers,
        "occupied_ev_chargers": occupied_ev_chargers,
        "offline_ev_chargers": offline_ev_chargers,
        "maintenance_ev_chargers": maintenance_ev_chargers
    }
