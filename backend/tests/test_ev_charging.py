from datetime import (
    datetime,
    timedelta,
    timezone,
)
from decimal import Decimal

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.reservation_service import (
    check_in_reservation,
    check_out_reservation,
)
from app.utils.security import (
    create_access_token,
    hash_password,
)


def create_user(
    db_session,
    *,
    email,
    role="user",
):
    user = User(
        full_name=(
            "EV Administrator"
            if role == "admin"
            else "EV Test User"
        ),
        email=email,
        hashed_password=hash_password(
            "SmartParkTest123!"
        ),
        role=role,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def auth_headers(user):
    token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "role": user.role,
            "email": user.email,
        },
    )

    return {
        "Authorization":
            f"Bearer {token}"
    }


def create_location(
    db_session,
    *,
    total_spaces=4,
):
    location = ParkingLocation(
        name="EV Test Parking",
        address="50 Electric Road",
        city="London",
        postcode="E1 5EV",
        latitude=51.520,
        longitude=-0.070,
        total_spaces=total_spaces,
        hourly_rate=Decimal("4.00"),
        opening_time=None,
        closing_time=None,
        is_24_hours=True,
        is_active=True,
    )

    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)

    return location


def create_space(
    db_session,
    location,
    *,
    number,
    has_ev_charging=False,
    ev_status=None,
):
    space = ParkingSpace(
        parking_location_id=location.id,
        space_number=number,
        space_type="standard",
        is_available=True,
        has_ev_charging=has_ev_charging,
        ev_charger_status=ev_status,
        ev_charger_updated_at=(
            datetime.now(timezone.utc)
            if ev_status
            else None
        ),
        is_accessible=False,
        is_active=True,
    )

    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)

    return space


def test_public_availability_returns_ev_charger_counts(
    client,
    db_session,
):
    location = create_location(
        db_session,
        total_spaces=4,
    )

    create_space(
        db_session,
        location,
        number="EV1",
        has_ev_charging=True,
        ev_status="available",
    )

    create_space(
        db_session,
        location,
        number="EV2",
        has_ev_charging=True,
        ev_status="occupied",
    )

    create_space(
        db_session,
        location,
        number="EV3",
        has_ev_charging=True,
        ev_status="maintenance",
    )

    create_space(
        db_session,
        location,
        number="A1",
    )

    response = client.get(
        (
            "/api/parking/locations/"
            f"{location.id}/availability"
        )
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["total_ev_chargers"] == 3
    assert payload["available_ev_chargers"] == 1
    assert payload["occupied_ev_chargers"] == 1
    assert payload["offline_ev_chargers"] == 0
    assert payload["maintenance_ev_chargers"] == 1


def test_admin_ev_space_defaults_to_available(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="ev.admin@smartpark.com",
        role="admin",
    )

    location = create_location(
        db_session,
        total_spaces=1,
    )

    response = client.post(
        (
            "/api/admin/parking/locations/"
            f"{location.id}/spaces"
        ),
        json={
            "space_number": "EV10",
            "space_type": "standard",
            "has_ev_charging": True,
            "is_accessible": False,
            "is_available": True,
            "is_active": True,
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["has_ev_charging"] is True
    assert (
        payload["ev_charger_status"]
        == "available"
    )
    assert (
        payload["ev_charger_updated_at"]
        is not None
    )


def test_non_ev_space_cannot_have_ev_status(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="invalid.ev.admin@smartpark.com",
        role="admin",
    )

    location = create_location(
        db_session,
        total_spaces=1,
    )

    response = client.post(
        (
            "/api/admin/parking/locations/"
            f"{location.id}/spaces"
        ),
        json={
            "space_number": "A10",
            "space_type": "standard",
            "has_ev_charging": False,
            "ev_charger_status": "available",
            "is_accessible": False,
            "is_available": True,
            "is_active": True,
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 409

    assert (
        response.json()["detail"]
        == (
            "A non-EV parking space "
            "cannot have an EV charger status."
        )
    )


def test_ev_status_tracks_check_in_and_check_out(
    db_session,
):
    user = create_user(
        db_session,
        email="ev.driver@smartpark.com",
    )

    location = create_location(
        db_session,
        total_spaces=1,
    )

    vehicle = Vehicle(
        user_id=user.id,
        registration_number="EV12345",
        make="Tesla",
        model="Model 3",
        colour="White",
        vehicle_type="car",
        is_default=True,
    )

    space = create_space(
        db_session,
        location,
        number="EV20",
        has_ev_charging=True,
        ev_status="available",
    )

    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)

    now = datetime.now(timezone.utc)

    reservation = Reservation(
        user_id=user.id,
        vehicle_id=vehicle.id,
        parking_location_id=location.id,
        parking_space_id=space.id,
        booking_code="SP-EVTRACK",
        reserved_from=(
            now - timedelta(minutes=5)
        ),
        reserved_until=(
            now + timedelta(hours=1)
        ),
        status="confirmed",
        estimated_cost=Decimal("4.00"),
    )

    db_session.add(reservation)
    db_session.commit()
    db_session.refresh(reservation)

    check_in_reservation(
        db=db_session,
        reservation=reservation,
    )

    db_session.refresh(space)

    assert space.is_available is False
    assert (
        space.ev_charger_status
        == "occupied"
    )
    assert (
        space.ev_charger_updated_at
        is not None
    )

    check_out_reservation(
        db=db_session,
        reservation=reservation,
        payment_method="card",
    )

    db_session.refresh(space)

    assert space.is_available is True
    assert (
        space.ev_charger_status
        == "available"
    )
