from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.models.parking_location import ParkingLocation
from app.models.parking_session import ParkingSession
from app.models.parking_space import ParkingSpace
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.utils.security import create_access_token, hash_password


def create_user(
    db_session,
    *,
    email="reservation.user@smartpark.com",
):
    user = User(
        full_name="Reservation Test User",
        email=email,
        hashed_password=hash_password(
            "SmartParkTest123!"
        ),
        role="user",
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
        "Authorization": f"Bearer {token}"
    }


def create_vehicle(
    db_session,
    user,
    *,
    registration="TEST123",
):
    vehicle = Vehicle(
        user_id=user.id,
        registration_number=registration,
        make="Toyota",
        model="Corolla",
        colour="Black",
        vehicle_type="car",
        is_default=True,
    )

    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)

    return vehicle


def create_location(db_session):
    location = ParkingLocation(
        name="Reservation Test Parking",
        address="50 Test Road",
        city="London",
        postcode="E1 2AB",
        latitude=51.515,
        longitude=-0.075,
        total_spaces=2,
        hourly_rate=Decimal("4.50"),
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
    number,
):
    space = ParkingSpace(
        parking_location_id=location.id,
        space_number=number,
        space_type="standard",
        is_available=True,
        has_ev_charging=False,
        is_accessible=False,
        is_active=True,
    )

    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)

    return space


def reservation_payload(
    vehicle,
    location,
    *,
    start=None,
    end=None,
):
    if start is None:
        start = (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        )

    if end is None:
        end = start + timedelta(hours=2)

    return {
        "vehicle_id": str(vehicle.id),
        "parking_location_id": str(location.id),
        "reserved_from": start.isoformat(),
        "reserved_until": end.isoformat(),
    }


def test_create_reservation_allocates_first_available_space(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)

    space_b = create_space(
        db_session,
        location,
        "B2",
    )
    space_a = create_space(
        db_session,
        location,
        "A1",
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == str(user.id)
    assert data["vehicle_id"] == str(vehicle.id)
    assert data["parking_location_id"] == str(
        location.id
    )

    assert data["parking_space_id"] == str(
        space_a.id
    )

    assert data["status"] == "confirmed"
    assert Decimal(
        data["estimated_cost"]
    ) == Decimal("9.00")

    assert data["booking_code"].startswith(
        "SP-"
    )

    assert str(space_b.id) != data[
        "parking_space_id"
    ]


def test_overlapping_reservation_is_rejected_when_no_space_left(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)

    create_space(
        db_session,
        location,
        "A1",
    )

    start = (
        datetime.now(timezone.utc)
        + timedelta(hours=1)
    )
    end = start + timedelta(hours=2)

    first = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert first.status_code == 201

    second = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start + timedelta(minutes=30),
            end=end + timedelta(minutes=30),
        ),
        headers=auth_headers(user),
    )

    assert second.status_code == 400
    assert second.json()["detail"] == (
        "No parking space is available "
        "for the selected time."
    )


def test_cancelled_reservation_releases_scheduled_space(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)
    space = create_space(
        db_session,
        location,
        "A1",
    )

    payload = reservation_payload(
        vehicle,
        location,
    )

    first = client.post(
        "/api/reservations",
        json=payload,
        headers=auth_headers(user),
    )

    assert first.status_code == 201

    reservation_id = first.json()["id"]

    cancel = client.patch(
        (
            f"/api/reservations/"
            f"{reservation_id}/cancel"
        ),
        headers=auth_headers(user),
    )

    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"
    assert cancel.json()["cancelled_at"] is not None

    second = client.post(
        "/api/reservations",
        json=payload,
        headers=auth_headers(user),
    )

    assert second.status_code == 201

    assert second.json()[
        "parking_space_id"
    ] == str(space.id)


def test_user_cannot_reserve_with_another_users_vehicle(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="owner1@smartpark.com",
    )

    other_user = create_user(
        db_session,
        email="owner2@smartpark.com",
    )

    other_vehicle = create_vehicle(
        db_session,
        other_user,
        registration="OTHER123",
    )

    location = create_location(db_session)
    create_space(
        db_session,
        location,
        "A1",
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            other_vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Vehicle does not belong "
        "to the current user."
    )


def test_reservation_list_is_limited_to_current_user(
    client,
    db_session,
):
    user_one = create_user(
        db_session,
        email="list1@smartpark.com",
    )
    user_two = create_user(
        db_session,
        email="list2@smartpark.com",
    )

    vehicle_one = create_vehicle(
        db_session,
        user_one,
        registration="LIST001",
    )
    vehicle_two = create_vehicle(
        db_session,
        user_two,
        registration="LIST002",
    )

    location = create_location(db_session)

    create_space(
        db_session,
        location,
        "A1",
    )
    create_space(
        db_session,
        location,
        "A2",
    )

    first = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle_one,
            location,
        ),
        headers=auth_headers(user_one),
    )

    second = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle_two,
            location,
        ),
        headers=auth_headers(user_two),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(
        "/api/reservations",
        headers=auth_headers(user_one),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == first.json()["id"]
    assert data[0]["user_id"] == str(
        user_one.id
    )


def test_check_in_creates_session_and_marks_space_occupied(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)
    create_space(
        db_session,
        location,
        "A1",
    )

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    assert create_response.status_code == 201

    created = create_response.json()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": created[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert check_in.status_code == 200

    data = check_in.json()

    assert data["status"] == "checked_in"
    assert data["checked_in_at"] is not None

    reservation = db_session.get(
        Reservation,
        created["id"],
    )
    db_session.refresh(reservation)

    space = db_session.get(
        ParkingSpace,
        reservation.parking_space_id,
    )
    db_session.refresh(space)

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    assert reservation.status == "checked_in"
    assert reservation.checked_in_at is not None
    assert space.is_available is False

    assert session is not None
    assert session.status == "active"
    assert session.ended_at is None


def test_card_checkout_completes_full_parking_lifecycle(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)
    create_space(
        db_session,
        location,
        "A1",
    )

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    created = create_response.json()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": created[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert check_in.status_code == 200

    reservation = db_session.get(
        Reservation,
        created["id"],
    )
    db_session.refresh(reservation)

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    two_hours_ago = (
        datetime.now(timezone.utc)
        - timedelta(hours=2)
    )

    reservation.checked_in_at = two_hours_ago
    session.started_at = two_hours_ago

    db_session.commit()

    checkout = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": "card"
        },
        headers=auth_headers(user),
    )

    assert checkout.status_code == 200

    data = checkout.json()

    assert data["status"] == "completed"
    assert data["payment_method"] == "card"

    assert data[
        "payment_reference"
    ].startswith("PAY-")

    assert Decimal(
        data["final_cost"]
    ) == Decimal("9.00")

    db_session.expire_all()

    reservation = db_session.get(
        Reservation,
        reservation.id,
    )

    space = db_session.get(
        ParkingSpace,
        reservation.parking_space_id,
    )

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    payment = db_session.scalar(
        select(Payment).where(
            Payment.reservation_id
            == reservation.id,
            Payment.transaction_type
            == "parking_charge",
        )
    )

    assert reservation.status == "completed"
    assert reservation.checked_out_at is not None
    assert reservation.final_cost == Decimal("9.00")

    assert space.is_available is True

    assert session is not None
    assert session.status == "completed"
    assert session.ended_at is not None
    assert session.duration_minutes >= 120
    assert session.final_cost == Decimal("9.00")

    assert payment is not None
    assert payment.payment_method == "card"
    assert payment.amount == Decimal("9.00")
    assert payment.status == "paid"


def test_checkout_before_check_in_is_rejected(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location = create_location(db_session)
    create_space(
        db_session,
        location,
        "A1",
    )

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    reservation_id = create_response.json()["id"]

    response = client.post(
        (
            f"/api/reservations/"
            f"{reservation_id}/check-out"
        ),
        json={
            "payment_method": "card"
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only a checked-in reservation "
        "can be checked out."
    )


def test_future_reservation_can_use_space_occupied_right_now(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="future.booking@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="FUTURE01",
    )

    location = create_location(
        db_session
    )

    space = create_space(
        db_session,
        location,
        "A1",
    )

    # The space is physically occupied now.
    space.is_available = False
    db_session.commit()

    # But the requested reservation is for tomorrow,
    # when there are no scheduled conflicts.
    start = (
        datetime.now(timezone.utc)
        + timedelta(days=1)
    )
    end = start + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 201

    assert response.json()[
        "parking_space_id"
    ] == str(space.id)


def test_current_reservation_cannot_use_physically_occupied_space(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="current.occupied@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="CURRENT01",
    )

    location = create_location(
        db_session
    )

    space = create_space(
        db_session,
        location,
        "A1",
    )

    # The space is physically occupied right now.
    space.is_available = False
    db_session.commit()

    start = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )
    end = (
        datetime.now(timezone.utc)
        + timedelta(hours=1)
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No parking space is available "
        "for the selected time."
    )


def test_current_reservation_cannot_use_physically_occupied_space(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="current.occupied@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="CURRENT01",
    )

    location = create_location(
        db_session
    )

    space = create_space(
        db_session,
        location,
        "A1",
    )

    # The space is physically occupied right now.
    space.is_available = False
    db_session.commit()

    start = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )
    end = (
        datetime.now(timezone.utc)
        + timedelta(hours=1)
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No parking space is available "
        "for the selected time."
    )


def test_checked_in_overstay_blocks_future_booking_of_same_space(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="overstay.owner@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="OVERSTAY1",
    )

    second_user = create_user(
        db_session,
        email="overstay.next@smartpark.com",
    )

    second_vehicle = create_vehicle(
        db_session,
        second_user,
        registration="OVERSTAY2",
    )

    location = create_location(
        db_session
    )

    space = create_space(
        db_session,
        location,
        "A1",
    )

    now = datetime.now(timezone.utc)

    # First driver is still physically parked even
    # though the booked reservation period has ended.
    existing_reservation = Reservation(
        user_id=user.id,
        vehicle_id=vehicle.id,
        parking_location_id=location.id,
        parking_space_id=space.id,
        booking_code="SP-OVERSTAY",
        reserved_from=now - timedelta(hours=3),
        reserved_until=now - timedelta(hours=1),
        status="checked_in",
        estimated_cost=Decimal("9.00"),
        checked_in_at=now - timedelta(hours=3),
    )

    space.is_available = False

    db_session.add(existing_reservation)
    db_session.commit()

    # A second user requests the same single space
    # for a future period.
    future_start = now + timedelta(minutes=30)
    future_end = future_start + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            second_vehicle,
            location,
            start=future_start,
            end=future_end,
        ),
        headers=auth_headers(second_user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No parking space is available "
        "for the selected time."
    )


def test_space_becomes_bookable_after_overstay_checkout(
    client,
    db_session,
):
    first_user = create_user(
        db_session,
        email="overstay.checkout1@smartpark.com",
    )

    first_vehicle = create_vehicle(
        db_session,
        first_user,
        registration="CHECKOUT1",
    )

    second_user = create_user(
        db_session,
        email="overstay.checkout2@smartpark.com",
    )

    second_vehicle = create_vehicle(
        db_session,
        second_user,
        registration="CHECKOUT2",
    )

    location = create_location(
        db_session
    )

    space = create_space(
        db_session,
        location,
        "A1",
    )

    # Create and check in the first reservation.
    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            first_vehicle,
            location,
        ),
        headers=auth_headers(first_user),
    )

    assert create_response.status_code == 201

    created = create_response.json()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": created[
                "booking_code"
            ]
        },
        headers=auth_headers(first_user),
    )

    assert check_in.status_code == 200

    reservation = db_session.get(
        Reservation,
        created["id"],
    )

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    now = datetime.now(timezone.utc)

    # Simulate an overstay: the reservation period
    # ended one hour ago, but the driver stayed.
    reservation.reserved_from = (
        now - timedelta(hours=3)
    )
    reservation.reserved_until = (
        now - timedelta(hours=1)
    )
    reservation.checked_in_at = (
        now - timedelta(hours=2)
    )

    session.started_at = (
        now - timedelta(hours=2)
    )

    db_session.commit()

    checkout = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": "card"
        },
        headers=auth_headers(first_user),
    )

    assert checkout.status_code == 200
    assert checkout.json()["status"] == "completed"

    db_session.expire_all()

    space = db_session.get(
        ParkingSpace,
        space.id,
    )

    assert space.is_available is True

    # Once checkout is complete, another user may
    # reserve the same space for a future period.
    future_start = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )
    future_end = (
        future_start
        + timedelta(hours=2)
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            second_vehicle,
            location,
            start=future_start,
            end=future_end,
        ),
        headers=auth_headers(second_user),
    )

    assert response.status_code == 201

    assert response.json()[
        "parking_space_id"
    ] == str(space.id)


def test_check_in_too_early_is_rejected(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="early.checkin@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="EARLY001",
    )

    location = create_location(
        db_session
    )

    create_space(
        db_session,
        location,
        "A1",
    )

    start = (
        datetime.now(timezone.utc)
        + timedelta(hours=3)
    )
    end = start + timedelta(hours=2)

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert create_response.status_code == 201

    response = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": create_response.json()[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Check-in is only allowed from "
        "15 minutes before the reservation starts."
    )


def test_check_in_after_reservation_end_is_rejected(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="expired.checkin@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="EXPIRED01",
    )

    location = create_location(
        db_session
    )

    create_space(
        db_session,
        location,
        "A1",
    )

    start = (
        datetime.now(timezone.utc)
        - timedelta(hours=3)
    )
    end = (
        datetime.now(timezone.utc)
        - timedelta(hours=1)
    )

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert create_response.status_code == 201

    response = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": create_response.json()[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "This reservation has expired "
        "and can no longer be checked in."
    )


def test_reservation_outside_opening_hours_is_rejected(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="closed.hours@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="CLOSED01",
    )

    location = create_location(
        db_session
    )

    location.is_24_hours = False
    location.opening_time = time(8, 0)
    location.closing_time = time(20, 0)

    db_session.commit()

    create_space(
        db_session,
        location,
        "A1",
    )

    london = ZoneInfo("Europe/London")

    tomorrow = (
        datetime.now(london).date()
        + timedelta(days=1)
    )

    start = datetime.combine(
        tomorrow,
        time(22, 0),
        tzinfo=london,
    )

    end = datetime.combine(
        tomorrow,
        time(23, 0),
        tzinfo=london,
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The selected reservation time "
        "is outside this parking location's "
        "opening hours."
    )


def test_reservation_within_normal_opening_hours_is_allowed(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="daytime.hours@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="DAYTIME1",
    )

    location = create_location(
        db_session
    )

    location.is_24_hours = False
    location.opening_time = time(8, 0)
    location.closing_time = time(20, 0)
    db_session.commit()

    create_space(
        db_session,
        location,
        "A1",
    )

    london = ZoneInfo("Europe/London")

    tomorrow = (
        datetime.now(london).date()
        + timedelta(days=1)
    )

    start = datetime.combine(
        tomorrow,
        time(10, 0),
        tzinfo=london,
    )

    end = datetime.combine(
        tomorrow,
        time(12, 0),
        tzinfo=london,
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 201


def test_reservation_within_overnight_opening_hours_is_allowed(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="overnight.hours@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="NIGHT001",
    )

    location = create_location(
        db_session
    )

    location.is_24_hours = False
    location.opening_time = time(20, 0)
    location.closing_time = time(6, 0)
    db_session.commit()

    create_space(
        db_session,
        location,
        "A1",
    )

    london = ZoneInfo("Europe/London")

    tomorrow = (
        datetime.now(london).date()
        + timedelta(days=1)
    )

    start = datetime.combine(
        tomorrow,
        time(23, 0),
        tzinfo=london,
    )

    end = datetime.combine(
        tomorrow + timedelta(days=1),
        time(2, 0),
        tzinfo=london,
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 201


def test_dynamic_pricing_stores_ai_booking_snapshot(
    client,
    db_session,
    monkeypatch,
):
    user = create_user(
        db_session
    )

    vehicle = create_vehicle(
        db_session,
        user,
    )

    location = create_location(
        db_session
    )

    location.dynamic_pricing_enabled = True

    create_space(
        db_session,
        location,
        "A1",
    )

    create_space(
        db_session,
        location,
        "A2",
    )

    db_session.commit()

    # Make the AI result deterministic so
    # this integration test is reproducible.
    monkeypatch.setattr(
        (
            "app.services."
            "reservation_service."
            "predictor_v2.predict"
        ),
        lambda **kwargs: 90.0,
    )

    start = (
        datetime.now(timezone.utc)
        + timedelta(days=1)
    )

    end = (
        start
        + timedelta(hours=2)
    )

    response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
            start=start,
            end=end,
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 201

    data = response.json()

    assert Decimal(
        data["base_hourly_rate"]
    ) == Decimal("4.50")

    assert Decimal(
        data[
            "current_occupancy_at_booking"
        ]
    ) == Decimal("0.00")

    assert Decimal(
        data[
            "predicted_occupancy_at_booking"
        ]
    ) == Decimal("90.00")

    assert (
        data["pricing_model_version"]
        is not None
    )

    applied_rate = Decimal(
        data["applied_hourly_rate"]
    )

    multiplier = Decimal(
        data["pricing_multiplier"]
    )

    assert applied_rate != Decimal(
        "4.50"
    )

    assert multiplier != Decimal(
        "1.0000"
    )

    expected_cost = (
        applied_rate
        * Decimal("2")
    ).quantize(
        Decimal("0.01")
    )

    assert Decimal(
        data["estimated_cost"]
    ) == expected_cost

    reservation = db_session.get(
        Reservation,
        data["id"],
    )

    assert reservation is not None

    assert (
        reservation.base_hourly_rate
        == Decimal("4.50")
    )

    assert (
        reservation.applied_hourly_rate
        == applied_rate
    )

    assert (
        reservation.predicted_occupancy_at_booking
        == Decimal("90.00")
    )



def test_dynamic_pricing_rate_remains_locked_at_checkout(
    client,
    db_session,
    monkeypatch,
):
    from app.services.pricing_service import (
        calculate_estimated_cost,
    )

    user = create_user(
        db_session,
        email="dynamic.lock@smartpark.com",
    )

    vehicle = create_vehicle(
        db_session,
        user,
        registration="DYNAMIC1",
    )

    location = create_location(
        db_session
    )

    location.dynamic_pricing_enabled = True

    create_space(
        db_session,
        location,
        "A1",
    )

    db_session.commit()

    # Deterministic AI prediction for this
    # integration test.
    monkeypatch.setattr(
        (
            "app.services."
            "reservation_service."
            "predictor_v2.predict"
        ),
        lambda **kwargs: 90.0,
    )

    create_response = client.post(
        "/api/reservations",
        json=reservation_payload(
            vehicle,
            location,
        ),
        headers=auth_headers(user),
    )

    assert create_response.status_code == 201

    created = create_response.json()

    locked_rate = Decimal(
        created["applied_hourly_rate"]
    )

    assert locked_rate > Decimal("0")

    reservation = db_session.get(
        Reservation,
        created["id"],
    )

    assert (
        reservation.applied_hourly_rate
        == locked_rate
    )

    # Simulate an admin changing the base
    # parking rate after the customer booked.
    location.hourly_rate = Decimal(
        "99.00"
    )

    db_session.commit()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code":
                created["booking_code"]
        },
        headers=auth_headers(user),
    )

    assert check_in.status_code == 200

    db_session.expire_all()

    reservation = db_session.get(
        Reservation,
        created["id"],
    )

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    two_hours_ago = (
        datetime.now(timezone.utc)
        - timedelta(hours=2)
    )

    reservation.checked_in_at = (
        two_hours_ago
    )

    session.started_at = (
        two_hours_ago
    )

    db_session.commit()

    checkout = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": "card"
        },
        headers=auth_headers(user),
    )

    assert checkout.status_code == 200

    data = checkout.json()

    db_session.expire_all()

    reservation = db_session.get(
        Reservation,
        reservation.id,
    )

    expected_locked_cost = (
        calculate_estimated_cost(
            reserved_from=(
                reservation.checked_in_at
            ),
            reserved_until=(
                reservation.checked_out_at
            ),
            hourly_rate=locked_rate,
        )
    )

    changed_rate_cost = (
        calculate_estimated_cost(
            reserved_from=(
                reservation.checked_in_at
            ),
            reserved_until=(
                reservation.checked_out_at
            ),
            hourly_rate=Decimal(
                "99.00"
            ),
        )
    )

    assert Decimal(
        data["final_cost"]
    ) == expected_locked_cost

    assert (
        reservation.final_cost
        == expected_locked_cost
    )

    assert (
        reservation.applied_hourly_rate
        == locked_rate
    )

    assert (
        expected_locked_cost
        != changed_rate_cost
    )
