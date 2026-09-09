import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.schemas.admin_parking import (
    AdminParkingLocationCreate,
    AdminParkingLocationUpdate,
    AdminParkingSpaceCreate,
    AdminParkingSpaceUpdate
)


ACTIVE_RESERVATION_STATUSES = {
    "confirmed",
    "checked_in"
}


def get_all_admin_parking_locations(
    db: Session
) -> list[ParkingLocation]:
    statement = (
        select(ParkingLocation)
        .order_by(ParkingLocation.name)
    )

    return list(
        db.scalars(statement).all()
    )


def get_admin_parking_location_by_id(
    db: Session,
    parking_location_id: uuid.UUID
) -> ParkingLocation | None:
    return db.get(
        ParkingLocation,
        parking_location_id
    )


def location_name_exists(
    db: Session,
    name: str,
    exclude_id: uuid.UUID | None = None
) -> bool:
    statement = select(ParkingLocation).where(
        func.lower(ParkingLocation.name)
        == name.strip().lower()
    )

    if exclude_id:
        statement = statement.where(
            ParkingLocation.id != exclude_id
        )

    return db.scalar(statement) is not None


def sync_location_capacity(
    db: Session,
    parking_location_id: uuid.UUID
) -> int:
    total_active_spaces = int(
        db.scalar(
            select(
                func.count(ParkingSpace.id)
            ).where(
                ParkingSpace.parking_location_id
                == parking_location_id,
                ParkingSpace.is_active.is_(True)
            )
        )
        or 0
    )

    location = db.get(
        ParkingLocation,
        parking_location_id
    )

    if location:
        location.total_spaces = total_active_spaces

    return total_active_spaces


def create_admin_parking_location(
    db: Session,
    location_data: AdminParkingLocationCreate
) -> ParkingLocation:

    if location_name_exists(
        db,
        location_data.name
    ):
        raise ValueError(
            "A parking location with this name already exists."
        )

    opening_time = location_data.opening_time
    closing_time = location_data.closing_time

    if location_data.is_24_hours:
        opening_time = None
        closing_time = None

    location = ParkingLocation(
        name=location_data.name.strip(),
        address=location_data.address.strip(),
        city=location_data.city.strip(),
        postcode=location_data.postcode.strip(),
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        total_spaces=location_data.initial_spaces,
        hourly_rate=location_data.hourly_rate,
        opening_time=opening_time,
        closing_time=closing_time,
        is_24_hours=location_data.is_24_hours,
        is_active=location_data.is_active
    )

    db.add(location)
    db.flush()

    width = max(
        3,
        len(str(location_data.initial_spaces))
    )

    for number in range(
        1,
        location_data.initial_spaces + 1
    ):
        parking_space = ParkingSpace(
            parking_location_id=location.id,
            space_number=str(number).zfill(width),
            space_type="standard",
            is_available=True,
            has_ev_charging=False,
            is_accessible=False,
            is_active=True
        )

        db.add(parking_space)

    db.flush()

    sync_location_capacity(
        db=db,
        parking_location_id=location.id
    )

    db.commit()
    db.refresh(location)

    return location


def update_admin_parking_location(
    db: Session,
    location: ParkingLocation,
    location_data: AdminParkingLocationUpdate
) -> ParkingLocation:

    updates = location_data.model_dump(
        exclude_unset=True
    )

    if "name" in updates:
        new_name = updates["name"].strip()

        if location_name_exists(
            db=db,
            name=new_name,
            exclude_id=location.id
        ):
            raise ValueError(
                "A parking location with this name already exists."
            )

        updates["name"] = new_name

    for field in (
        "address",
        "city",
        "postcode"
    ):
        if field in updates:
            updates[field] = updates[field].strip()

    final_is_24_hours = updates.get(
        "is_24_hours",
        location.is_24_hours
    )

    final_opening_time = updates.get(
        "opening_time",
        location.opening_time
    )

    final_closing_time = updates.get(
        "closing_time",
        location.closing_time
    )

    if final_is_24_hours:
        updates["opening_time"] = None
        updates["closing_time"] = None

    else:
        if (
            final_opening_time is None
            or final_closing_time is None
        ):
            raise ValueError(
                "Opening and closing times are required "
                "for a non-24-hour parking location."
            )

        if final_opening_time == final_closing_time:
            raise ValueError(
                "Opening and closing times cannot be identical."
            )

    for field, value in updates.items():
        setattr(
            location,
            field,
            value
        )

    db.commit()
    db.refresh(location)

    return location


def set_parking_location_status(
    db: Session,
    location: ParkingLocation,
    is_active: bool
) -> ParkingLocation:

    if not is_active:
        active_reservations = int(
            db.scalar(
                select(
                    func.count(Reservation.id)
                ).where(
                    Reservation.parking_location_id
                    == location.id,
                    Reservation.status.in_(
                        ACTIVE_RESERVATION_STATUSES
                    )
                )
            )
            or 0
        )

        if active_reservations > 0:
            raise ValueError(
                "This parking location cannot be deactivated "
                "while it has active reservations."
            )

    location.is_active = is_active

    db.commit()
    db.refresh(location)

    return location


def get_admin_parking_spaces(
    db: Session,
    parking_location_id: uuid.UUID
) -> list[ParkingSpace]:

    statement = (
        select(ParkingSpace)
        .where(
            ParkingSpace.parking_location_id
            == parking_location_id
        )
        .order_by(
            ParkingSpace.space_number
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_admin_parking_space_by_id(
    db: Session,
    parking_space_id: uuid.UUID
) -> ParkingSpace | None:
    return db.get(
        ParkingSpace,
        parking_space_id
    )


def space_number_exists(
    db: Session,
    parking_location_id: uuid.UUID,
    space_number: str,
    exclude_id: uuid.UUID | None = None
) -> bool:

    statement = select(ParkingSpace).where(
        ParkingSpace.parking_location_id
        == parking_location_id,

        func.lower(ParkingSpace.space_number)
        == space_number.strip().lower()
    )

    if exclude_id:
        statement = statement.where(
            ParkingSpace.id != exclude_id
        )

    return db.scalar(statement) is not None


def create_admin_parking_space(
    db: Session,
    parking_location: ParkingLocation,
    space_data: AdminParkingSpaceCreate
) -> ParkingSpace:

    space_number = (
        space_data.space_number
        .strip()
        .upper()
    )

    if space_number_exists(
        db=db,
        parking_location_id=parking_location.id,
        space_number=space_number
    ):
        raise ValueError(
            "This parking space number already exists "
            "at the selected location."
        )

    if (
        not space_data.has_ev_charging
        and space_data.ev_charger_status is not None
    ):
        raise ValueError(
            "A non-EV parking space cannot have "
            "an EV charger status."
        )

    ev_charger_status = None
    ev_charger_updated_at = None

    if space_data.has_ev_charging:
        ev_charger_status = (
            space_data.ev_charger_status
            or "available"
        )
        ev_charger_updated_at = (
            datetime.now(timezone.utc)
        )

    parking_space = ParkingSpace(
        parking_location_id=parking_location.id,
        space_number=space_number,
        space_type=space_data.space_type,
        is_available=space_data.is_available,
        has_ev_charging=space_data.has_ev_charging,
        ev_charger_status=ev_charger_status,
        ev_charger_updated_at=ev_charger_updated_at,
        is_accessible=space_data.is_accessible,
        is_active=space_data.is_active
    )

    db.add(parking_space)
    db.flush()

    sync_location_capacity(
        db=db,
        parking_location_id=parking_location.id
    )

    db.commit()
    db.refresh(parking_space)

    return parking_space


def update_admin_parking_space(
    db: Session,
    parking_space: ParkingSpace,
    space_data: AdminParkingSpaceUpdate
) -> ParkingSpace:

    updates = space_data.model_dump(
        exclude_unset=True
    )

    if "space_number" in updates:
        new_space_number = (
            updates["space_number"]
            .strip()
            .upper()
        )

        if space_number_exists(
            db=db,
            parking_location_id=(
                parking_space.parking_location_id
            ),
            space_number=new_space_number,
            exclude_id=parking_space.id
        ):
            raise ValueError(
                "This parking space number already exists "
                "at the selected location."
            )

        updates[
            "space_number"
        ] = new_space_number

    effective_has_ev = updates.get(
        "has_ev_charging",
        parking_space.has_ev_charging
    )

    if not effective_has_ev:
        if (
            "ev_charger_status" in updates
            and updates["ev_charger_status"] is not None
        ):
            raise ValueError(
                "A non-EV parking space cannot have "
                "an EV charger status."
            )

        updates["ev_charger_status"] = None
        updates["ev_charger_updated_at"] = None

    else:
        charger_status_changed = (
            "ev_charger_status" in updates
        )

        enabling_ev = (
            updates.get("has_ev_charging") is True
            and not parking_space.has_ev_charging
        )

        if charger_status_changed:
            if updates["ev_charger_status"] is None:
                raise ValueError(
                    "EV charger status is required "
                    "for an EV charging space."
                )

            updates["ev_charger_updated_at"] = (
                datetime.now(timezone.utc)
            )

        elif enabling_ev:
            updates["ev_charger_status"] = (
                "available"
            )
            updates["ev_charger_updated_at"] = (
                datetime.now(timezone.utc)
            )

    if (
        updates.get("is_active") is False
    ):
        active_reservation = db.scalar(
            select(Reservation).where(
                Reservation.parking_space_id
                == parking_space.id,
                Reservation.status.in_(
                    ACTIVE_RESERVATION_STATUSES
                )
            )
        )

        if active_reservation:
            raise ValueError(
                "This parking space cannot be deactivated "
                "while it has an active reservation."
            )

    for field, value in updates.items():
        setattr(
            parking_space,
            field,
            value
        )

    db.flush()

    sync_location_capacity(
        db=db,
        parking_location_id=(
            parking_space.parking_location_id
        )
    )

    db.commit()
    db.refresh(parking_space)

    return parking_space
