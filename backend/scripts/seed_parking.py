from datetime import time

from sqlalchemy import select

from app.database import SessionLocal
from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace


PARKING_LOCATIONS = [
    {
        "name": "SmartPark Liverpool Street Hub",
        "address": "Liverpool Street",
        "city": "London",
        "postcode": "EC2M 7PY",
        "latitude": 51.5175,
        "longitude": -0.0826,
        "total_spaces": 40,
        "hourly_rate": 4.50,
        "opening_time": time(6, 0),
        "closing_time": time(23, 30),
        "is_24_hours": False,
    },
    {
        "name": "SmartPark Stratford Central",
        "address": "Stratford Centre",
        "city": "London",
        "postcode": "E15 1XE",
        "latitude": 51.5416,
        "longitude": -0.0039,
        "total_spaces": 55,
        "hourly_rate": 3.20,
        "opening_time": None,
        "closing_time": None,
        "is_24_hours": True,
    },
    {
        "name": "SmartPark Canary Wharf Riverside",
        "address": "Canary Wharf",
        "city": "London",
        "postcode": "E14 5AB",
        "latitude": 51.5054,
        "longitude": -0.0235,
        "total_spaces": 35,
        "hourly_rate": 5.00,
        "opening_time": time(5, 30),
        "closing_time": time(23, 59),
        "is_24_hours": False,
    },
]


def create_spaces(db, location):
    existing_spaces = db.scalars(
        select(ParkingSpace).where(
            ParkingSpace.parking_location_id == location.id
        )
    ).all()

    if existing_spaces:
        print(f"Spaces already exist for {location.name}")
        return

    for number in range(1, location.total_spaces + 1):

        if number <= 2:
            space_type = "accessible"
            is_accessible = True
            has_ev_charging = False

        elif number <= 7:
            space_type = "ev"
            is_accessible = False
            has_ev_charging = True

        else:
            space_type = "standard"
            is_accessible = False
            has_ev_charging = False

        # Deterministic demonstration occupancy.
        # Every fourth space begins as occupied.
        is_available = number % 4 != 0

        parking_space = ParkingSpace(
            parking_location_id=location.id,
            space_number=f"{number:03}",
            space_type=space_type,
            is_available=is_available,
            has_ev_charging=has_ev_charging,
            is_accessible=is_accessible,
            is_active=True
        )

        db.add(parking_space)


def seed():
    db = SessionLocal()

    try:
        for data in PARKING_LOCATIONS:
            existing_location = db.scalar(
                select(ParkingLocation).where(
                    ParkingLocation.name == data["name"]
                )
            )

            if existing_location:
                location = existing_location
                print(f"Location already exists: {location.name}")

            else:
                location = ParkingLocation(
                    **data,
                    is_active=True
                )

                db.add(location)
                db.flush()

                print(f"Created location: {location.name}")

            create_spaces(db, location)

        db.commit()

        print("\nSmartPark AI parking seed completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
