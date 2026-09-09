import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


def _clear_other_defaults(
    db: Session,
    user_id,
    exclude_vehicle_id: uuid.UUID | None = None
) -> None:
    statement = select(Vehicle).where(
        Vehicle.user_id == user_id,
        Vehicle.is_default == True
    )

    if exclude_vehicle_id is not None:
        statement = statement.where(
            Vehicle.id != exclude_vehicle_id
        )

    existing_defaults = db.scalars(
        statement
    ).all()

    for existing in existing_defaults:
        existing.is_default = False


def _get_another_vehicle(
    db: Session,
    user_id,
    exclude_vehicle_id: uuid.UUID | None = None
) -> Vehicle | None:
    statement = select(Vehicle).where(
        Vehicle.user_id == user_id
    )

    if exclude_vehicle_id is not None:
        statement = statement.where(
            Vehicle.id != exclude_vehicle_id
        )

    statement = statement.limit(1)

    return db.scalar(statement)


def create_vehicle(
    db: Session,
    user_id,
    vehicle_data: VehicleCreate
) -> Vehicle:
    existing_vehicle = _get_another_vehicle(
        db=db,
        user_id=user_id
    )

    # The first vehicle must always become default.
    should_be_default = (
        vehicle_data.is_default
        or existing_vehicle is None
    )

    if should_be_default:
        _clear_other_defaults(
            db=db,
            user_id=user_id
        )

    vehicle = Vehicle(
        user_id=user_id,
        registration_number=(
            vehicle_data.registration_number
            .upper()
            .strip()
        ),
        make=vehicle_data.make.strip(),
        model=vehicle_data.model.strip(),
        colour=vehicle_data.colour.strip(),
        vehicle_type=(
            vehicle_data.vehicle_type
            .lower()
            .strip()
        ),
        is_default=should_be_default
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def get_user_vehicles(
    db: Session,
    user_id
) -> list[Vehicle]:
    statement = (
        select(Vehicle)
        .where(
            Vehicle.user_id == user_id
        )
        .order_by(
            Vehicle.is_default.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_user_vehicle_by_id(
    db: Session,
    user_id,
    vehicle_id: uuid.UUID
) -> Vehicle | None:
    statement = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.user_id == user_id
    )

    return db.scalar(statement)


def update_vehicle(
    db: Session,
    vehicle: Vehicle,
    vehicle_data: VehicleUpdate
) -> Vehicle:
    updates = vehicle_data.model_dump(
        exclude_unset=True
    )

    was_default = vehicle.is_default

    if updates.get("is_default") is True:
        _clear_other_defaults(
            db=db,
            user_id=vehicle.user_id,
            exclude_vehicle_id=vehicle.id
        )

    for field, value in updates.items():
        if (
            field == "registration_number"
            and value is not None
        ):
            value = (
                value.upper().strip()
            )

        elif (
            field in {
                "make",
                "model",
                "colour"
            }
            and value is not None
        ):
            value = value.strip()

        elif (
            field == "vehicle_type"
            and value is not None
        ):
            value = (
                value.lower().strip()
            )

        setattr(
            vehicle,
            field,
            value
        )

    # Never leave an account with vehicles
    # but without a default vehicle.
    if (
        was_default
        and updates.get("is_default")
        is False
    ):
        replacement = _get_another_vehicle(
            db=db,
            user_id=vehicle.user_id,
            exclude_vehicle_id=vehicle.id
        )

        if replacement is None:
            vehicle.is_default = True
        else:
            replacement.is_default = True

    db.commit()
    db.refresh(vehicle)

    return vehicle


def delete_vehicle(
    db: Session,
    vehicle: Vehicle
) -> None:
    user_id = vehicle.user_id
    vehicle_id = vehicle.id
    was_default = vehicle.is_default

    db.delete(vehicle)
    db.flush()

    if was_default:
        replacement = _get_another_vehicle(
            db=db,
            user_id=user_id,
            exclude_vehicle_id=vehicle_id
        )

        if replacement is not None:
            replacement.is_default = True

    db.commit()
