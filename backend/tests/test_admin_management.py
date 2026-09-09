from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.models.review import Review
from app.models.user import User
from app.models.vehicle import Vehicle
from app.utils.security import (
    create_access_token,
    hash_password,
)


def create_user(
    db_session,
    *,
    email,
    role="user",
    is_active=True,
    name=None,
):
    user = User(
        full_name=(
            name
            or (
                "Admin Test Administrator"
                if role == "admin"
                else "Admin Test User"
            )
        ),
        email=email,
        hashed_password=hash_password(
            "SmartParkTest123!"
        ),
        role=role,
        is_active=is_active,
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


def create_parking_setup(
    db_session,
    user,
):
    vehicle = Vehicle(
        user_id=user.id,
        registration_number="ADM123",
        make="Tesla",
        model="Model 3",
        colour="Black",
        vehicle_type="car",
        is_default=True,
    )

    location = ParkingLocation(
        name="Admin Test Parking",
        address="10 Admin Street",
        city="London",
        postcode="E1 1AA",
        latitude=51.515,
        longitude=-0.075,
        total_spaces=1,
        hourly_rate=Decimal(
            "4.50"
        ),
        opening_time=None,
        closing_time=None,
        is_24_hours=True,
        is_active=True,
    )

    db_session.add_all([
        vehicle,
        location,
    ])
    db_session.commit()

    db_session.refresh(vehicle)
    db_session.refresh(location)

    space = ParkingSpace(
        parking_location_id=
            location.id,
        space_number="A001",
        space_type="standard",
        is_available=True,
        has_ev_charging=False,
        is_accessible=False,
        is_active=True,
    )

    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)

    return (
        vehicle,
        location,
        space,
    )


def test_admin_can_list_and_update_users(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="users.admin@smartpark.com",
        role="admin",
    )

    target = create_user(
        db_session,
        email="users.target@smartpark.com",
    )

    response = client.get(
        "/api/admin/users",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    users = response.json()

    target_record = next(
        item
        for item in users
        if item["email"]
        == target.email
    )

    assert (
        target_record["is_active"]
        is True
    )

    response = client.patch(
        (
            "/api/admin/users/"
            f"{target.id}/status"
        ),
        json={
            "is_active": False,
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    assert (
        response.json()["is_active"]
        is False
    )

    db_session.refresh(target)

    assert target.is_active is False


def test_admin_cannot_deactivate_self(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="self.admin@smartpark.com",
        role="admin",
    )

    response = client.patch(
        (
            "/api/admin/users/"
            f"{admin.id}/status"
        ),
        json={
            "is_active": False,
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 400

    db_session.refresh(admin)

    assert admin.is_active is True


def test_admin_can_list_reservations_with_joined_details(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email=(
            "reservations.admin"
            "@smartpark.com"
        ),
        role="admin",
    )

    user = create_user(
        db_session,
        email=(
            "reservations.user"
            "@smartpark.com"
        ),
        name="Reservation Test User",
    )

    (
        vehicle,
        location,
        space,
    ) = create_parking_setup(
        db_session,
        user,
    )

    start = (
        datetime.now(timezone.utc)
        + timedelta(hours=1)
    )

    reservation = Reservation(
        user_id=user.id,
        vehicle_id=vehicle.id,
        parking_location_id=
            location.id,
        parking_space_id=space.id,
        booking_code="SP-ADMINTEST",
        reserved_from=start,
        reserved_until=(
            start
            + timedelta(hours=2)
        ),
        status="confirmed",
        estimated_cost=Decimal(
            "9.00"
        ),
    )

    db_session.add(reservation)
    db_session.commit()

    response = client.get(
        "/api/admin/reservations",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    records = response.json()

    assert len(records) == 1

    record = records[0]

    assert (
        record["booking_code"]
        == "SP-ADMINTEST"
    )
    assert (
        record["user_email"]
        == user.email
    )
    assert (
        record[
            "vehicle_registration"
        ]
        == "ADM123"
    )
    assert (
        record[
            "parking_location_name"
        ]
        == "Admin Test Parking"
    )
    assert (
        record[
            "parking_space_number"
        ]
        == "A001"
    )


def test_admin_can_list_and_delete_reviews(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="reviews.admin@smartpark.com",
        role="admin",
    )

    user = create_user(
        db_session,
        email="reviews.user@smartpark.com",
        name="Review Test User",
    )

    (
        _vehicle,
        location,
        _space,
    ) = create_parking_setup(
        db_session,
        user,
    )

    review = Review(
        user_id=user.id,
        parking_location_id=
            location.id,
        rating=5,
        comment=(
            "Excellent parking "
            "location."
        ),
    )

    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    review_id = review.id

    response = client.get(
        "/api/admin/reviews",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    records = response.json()

    assert len(records) == 1
    assert records[0]["rating"] == 5
    assert (
        records[0]["user_email"]
        == user.email
    )
    assert (
        records[0][
            "parking_location_name"
        ]
        == "Admin Test Parking"
    )

    response = client.delete(
        (
            "/api/admin/reviews/"
            f"{review_id}"
        ),
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload[
            "deleted_review_id"
        ]
        == str(review_id)
    )
    assert (
        payload["message"]
        == (
            "Review removed "
            "successfully."
        )
    )

    deleted_review_id = (
        db_session.scalar(
            select(Review.id).where(
                Review.id
                == review_id
            )
        )
    )

    assert deleted_review_id is None


def test_admin_can_send_single_user_notification(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email=(
            "notifications.admin"
            "@smartpark.com"
        ),
        role="admin",
    )

    target = create_user(
        db_session,
        email=(
            "notifications.user"
            "@smartpark.com"
        ),
        name=(
            "Notification "
            "Test User"
        ),
    )

    response = client.post(
        "/api/admin/notifications/send",
        json={
            "recipient_mode":
                "single_user",
            "user_id":
                str(target.id),
            "title":
                "SmartPark Test",
            "message":
                (
                    "Administrative "
                    "notification test."
                ),
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 201
    assert (
        response.json()[
            "created_count"
        ]
        == 1
    )

    response = client.get(
        "/api/admin/notifications",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    records = response.json()

    assert len(records) == 1

    record = records[0]

    assert (
        record["user_email"]
        == target.email
    )
    assert (
        record[
            "notification_type"
        ]
        == "admin_announcement"
    )
    assert (
        record["title"]
        == "SmartPark Test"
    )
    assert record["is_read"] is False


def test_broadcast_targets_only_active_users(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email=(
            "broadcast.admin"
            "@smartpark.com"
        ),
        role="admin",
    )

    create_user(
        db_session,
        email=(
            "broadcast.active"
            "@smartpark.com"
        ),
        is_active=True,
    )

    create_user(
        db_session,
        email=(
            "broadcast.inactive"
            "@smartpark.com"
        ),
        is_active=False,
    )

    response = client.post(
        "/api/admin/notifications/send",
        json={
            "recipient_mode":
                "all_active",
            "title":
                "Service Notice",
            "message":
                (
                    "Broadcast "
                    "notification test."
                ),
        },
        headers=auth_headers(admin),
    )

    assert response.status_code == 201

    # Active recipients are:
    # the administrator + active user.
    assert (
        response.json()[
            "created_count"
        ]
        == 2
    )

    response = client.get(
        "/api/admin/notifications",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_can_list_payments(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email=(
            "payments.admin"
            "@smartpark.com"
        ),
        role="admin",
    )

    response = client.get(
        "/api/admin/payments",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_standard_user_cannot_access_admin_management_routes(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email=(
            "blocked.user"
            "@smartpark.com"
        ),
    )

    headers = auth_headers(user)

    routes = [
        "/api/admin/users",
        "/api/admin/reservations",
        "/api/admin/reviews",
        "/api/admin/notifications",
        "/api/admin/payments",
    ]

    for route in routes:
        response = client.get(
            route,
            headers=headers,
        )

        assert (
            response.status_code
            == 403
        )

        assert (
            response.json()["detail"]
            == (
                "Administrator access "
                "is required."
            )
        )
