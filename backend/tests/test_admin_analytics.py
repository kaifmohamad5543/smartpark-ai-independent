from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.parking_location import ParkingLocation
from app.models.parking_session import ParkingSession
from app.models.parking_space import ParkingSpace
from app.models.payment import Payment
from app.models.prediction import Prediction
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.utils.security import create_access_token, hash_password


def create_user(
    db_session,
    *,
    email,
    role="user",
    is_active=True,
):
    user = User(
        full_name=f"Analytics {role.title()}",
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
        "Authorization": f"Bearer {token}"
    }


def create_location(
    db_session,
    *,
    name,
    active=True,
):
    location = ParkingLocation(
        name=name,
        address="60 Analytics Road",
        city="London",
        postcode="E1 7AB",
        latitude=51.519,
        longitude=-0.074,
        total_spaces=4,
        hourly_rate=Decimal("4.00"),
        opening_time=None,
        closing_time=None,
        is_24_hours=True,
        is_active=active,
    )

    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)

    return location


def create_spaces(
    db_session,
    location,
    *,
    count,
    unavailable=0,
):
    spaces = []

    for index in range(1, count + 1):
        space = ParkingSpace(
            parking_location_id=location.id,
            space_number=f"S{index}",
            space_type="standard",
            is_available=index > unavailable,
            has_ev_charging=False,
            is_accessible=False,
            is_active=True,
        )

        db_session.add(space)
        spaces.append(space)

    db_session.commit()

    for space in spaces:
        db_session.refresh(space)

    return spaces


def create_vehicle(
    db_session,
    user,
):
    vehicle = Vehicle(
        user_id=user.id,
        registration_number="ANA123",
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


def add_reservation(
    db_session,
    *,
    user,
    vehicle,
    location,
    space,
    booking_code,
    status,
    final_cost=None,
):
    now = datetime.now(timezone.utc)

    reservation = Reservation(
        user_id=user.id,
        vehicle_id=vehicle.id,
        parking_location_id=location.id,
        parking_space_id=space.id,
        booking_code=booking_code,
        reserved_from=now,
        reserved_until=now + timedelta(hours=2),
        status=status,
        estimated_cost=Decimal("8.00"),
        final_cost=final_cost,
        checked_in_at=(
            now - timedelta(hours=2)
            if status in {
                "checked_in",
                "completed",
            }
            else None
        ),
        checked_out_at=(
            now
            if status == "completed"
            else None
        ),
        cancelled_at=(
            now
            if status == "cancelled"
            else None
        ),
        created_at=now,
    )

    db_session.add(reservation)
    db_session.commit()
    db_session.refresh(reservation)

    return reservation


def seed_core_analytics_data(db_session):
    admin = create_user(
        db_session,
        email="analytics.admin@smartpark.com",
        role="admin",
    )

    user = create_user(
        db_session,
        email="analytics.user@smartpark.com",
    )

    create_user(
        db_session,
        email="analytics.inactive@smartpark.com",
        is_active=False,
    )

    active_location = create_location(
        db_session,
        name="Active Analytics Parking",
        active=True,
    )

    inactive_location = create_location(
        db_session,
        name="Inactive Analytics Parking",
        active=False,
    )

    spaces = create_spaces(
        db_session,
        active_location,
        count=4,
        unavailable=1,
    )

    # These must not affect the overview because
    # their parent location is inactive.
    create_spaces(
        db_session,
        inactive_location,
        count=3,
        unavailable=3,
    )

    vehicle = create_vehicle(
        db_session,
        user,
    )

    confirmed = add_reservation(
        db_session,
        user=user,
        vehicle=vehicle,
        location=active_location,
        space=spaces[0],
        booking_code="SP-ANA0001",
        status="confirmed",
    )

    checked_in = add_reservation(
        db_session,
        user=user,
        vehicle=vehicle,
        location=active_location,
        space=spaces[1],
        booking_code="SP-ANA0002",
        status="checked_in",
    )

    cancelled = add_reservation(
        db_session,
        user=user,
        vehicle=vehicle,
        location=active_location,
        space=spaces[2],
        booking_code="SP-ANA0003",
        status="cancelled",
    )

    completed_refunded = add_reservation(
        db_session,
        user=user,
        vehicle=vehicle,
        location=active_location,
        space=spaces[2],
        booking_code="SP-ANA0004",
        status="completed",
        final_cost=Decimal("12.00"),
    )

    completed_paid = add_reservation(
        db_session,
        user=user,
        vehicle=vehicle,
        location=active_location,
        space=spaces[3],
        booking_code="SP-ANA0005",
        status="completed",
        final_cost=Decimal("4.00"),
    )

    session_one = ParkingSession(
        reservation_id=completed_refunded.id,
        user_id=user.id,
        parking_location_id=active_location.id,
        parking_space_id=spaces[2].id,
        started_at=datetime.now(timezone.utc)
        - timedelta(hours=3),
        ended_at=datetime.now(timezone.utc),
        duration_minutes=180,
        final_cost=Decimal("12.00"),
        status="completed",
    )

    session_two = ParkingSession(
        reservation_id=completed_paid.id,
        user_id=user.id,
        parking_location_id=active_location.id,
        parking_space_id=spaces[3].id,
        started_at=datetime.now(timezone.utc)
        - timedelta(hours=1),
        ended_at=datetime.now(timezone.utc),
        duration_minutes=60,
        final_cost=Decimal("4.00"),
        status="completed",
    )

    db_session.add_all([
        session_one,
        session_two,
    ])
    db_session.commit()
    db_session.refresh(session_one)
    db_session.refresh(session_two)

    refunded_charge = Payment(
        user_id=user.id,
        reservation_id=completed_refunded.id,
        parking_session_id=session_one.id,
        payment_reference="PAY-ANA000001",
        transaction_type="parking_charge",
        payment_method="wallet",
        amount=Decimal("12.00"),
        status="refunded",
        paid_at=datetime.now(timezone.utc),
    )

    paid_charge = Payment(
        user_id=user.id,
        reservation_id=completed_paid.id,
        parking_session_id=session_two.id,
        payment_reference="PAY-ANA000002",
        transaction_type="parking_charge",
        payment_method="card",
        amount=Decimal("4.00"),
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )

    db_session.add_all([
        refunded_charge,
        paid_charge,
    ])
    db_session.flush()

    refund = Payment(
        user_id=user.id,
        reservation_id=completed_refunded.id,
        parking_session_id=session_one.id,
        related_payment_id=refunded_charge.id,
        payment_reference="PAY-ANA000003",
        transaction_type="refund",
        payment_method="wallet",
        amount=Decimal("12.00"),
        status="refunded",
        paid_at=datetime.now(timezone.utc),
    )

    db_session.add(refund)
    db_session.commit()

    return {
        "admin": admin,
        "user": user,
        "location": active_location,
        "reservations": {
            "confirmed": confirmed,
            "checked_in": checked_in,
            "cancelled": cancelled,
            "completed_refunded":
                completed_refunded,
            "completed_paid":
                completed_paid,
        },
    }


def add_prediction(
    db_session,
    *,
    user,
    location,
    occupancy,
    code,
):
    prediction = Prediction(
        user_id=user.id,
        parking_location_id=location.id,
        hour=17,
        day_of_week=4,
        previous_occupancy=25.0,
        traffic_level=2,
        weather=1,
        event_level=1,
        parking_price=Decimal("4.00"),
        available_spaces=3,
        predicted_occupancy=occupancy,
        predicted_availability=round(
            100.0 - occupancy,
            2,
        ),
    )

    db_session.add(prediction)
    db_session.commit()
    db_session.refresh(prediction)

    return prediction


def test_standard_user_cannot_access_admin_analytics(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="analytics.denied@smartpark.com",
    )

    response = client.get(
        "/api/admin/analytics/overview",
        headers=auth_headers(user),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Administrator access is required."
    )


def test_overview_reports_counts_occupancy_and_net_revenue(
    client,
    db_session,
):
    seeded = seed_core_analytics_data(
        db_session
    )

    add_prediction(
        db_session,
        user=seeded["user"],
        location=seeded["location"],
        occupancy=40.0,
        code="1",
    )

    add_prediction(
        db_session,
        user=seeded["user"],
        location=seeded["location"],
        occupancy=60.0,
        code="2",
    )

    response = client.get(
        "/api/admin/analytics/overview",
        headers=auth_headers(
            seeded["admin"]
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_users"] == 3
    assert data["active_users"] == 2

    assert data["total_reservations"] == 5
    assert data["confirmed_reservations"] == 1
    assert data["checked_in_reservations"] == 1
    assert data["cancelled_reservations"] == 1
    assert data["completed_reservations"] == 2

    assert data[
        "completed_parking_sessions"
    ] == 2

    # £12 refunded + £4 retained.
    assert data["total_revenue"] == 4.0

    # Inactive parent location and its spaces
    # must be excluded.
    assert data[
        "total_parking_locations"
    ] == 1

    assert data[
        "total_parking_spaces"
    ] == 4

    assert data[
        "available_parking_spaces"
    ] == 3

    assert data[
        "overall_occupancy_percentage"
    ] == 25.0

    assert data["total_predictions"] == 2

    assert data[
        "average_predicted_occupancy"
    ] == 50.0


def test_location_performance_uses_net_payment_revenue(
    client,
    db_session,
):
    seeded = seed_core_analytics_data(
        db_session
    )

    add_prediction(
        db_session,
        user=seeded["user"],
        location=seeded["location"],
        occupancy=55.0,
        code="1",
    )

    response = client.get(
        "/api/admin/analytics/locations",
        headers=auth_headers(
            seeded["admin"]
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    location = data[0]

    assert location[
        "parking_location_id"
    ] == str(seeded["location"].id)

    assert location["total_spaces"] == 4
    assert location["available_spaces"] == 3

    assert location[
        "current_occupancy_percentage"
    ] == 25.0

    assert location[
        "total_reservations"
    ] == 5

    assert location[
        "completed_reservations"
    ] == 2

    assert location[
        "cancelled_reservations"
    ] == 1

    assert location[
        "completed_sessions"
    ] == 2

    assert location["total_revenue"] == 4.0

    assert location[
        "average_predicted_occupancy"
    ] == 55.0


def test_reservation_trends_returns_requested_days_and_today_counts(
    client,
    db_session,
):
    seeded = seed_core_analytics_data(
        db_session
    )

    response = client.get(
        (
            "/api/admin/analytics/"
            "reservation-trends?days=3"
        ),
        headers=auth_headers(
            seeded["admin"]
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3

    today = data[-1]

    assert today[
        "total_reservations"
    ] == 5

    assert today["confirmed"] == 1
    assert today["checked_in"] == 1
    assert today["completed"] == 2
    assert today["cancelled"] == 1


def test_ai_demand_analytics_classifies_all_demand_levels(
    client,
    db_session,
):
    seeded = seed_core_analytics_data(
        db_session
    )

    for index, occupancy in enumerate(
        [
            20.0,
            50.0,
            75.0,
            90.0,
        ],
        start=1,
    ):
        add_prediction(
            db_session,
            user=seeded["user"],
            location=seeded["location"],
            occupancy=occupancy,
            code=str(index),
        )

    response = client.get(
        (
            "/api/admin/analytics/"
            "ai-demand?limit=10"
        ),
        headers=auth_headers(
            seeded["admin"]
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_predictions"] == 4

    assert data[
        "average_predicted_occupancy"
    ] == 58.75

    assert data["low_demand_count"] == 1
    assert data["medium_demand_count"] == 1
    assert data["high_demand_count"] == 1
    assert data[
        "very_high_demand_count"
    ] == 1

    assert len(
        data["recent_predictions"]
    ) == 4

    levels = {
        item["demand_level"]
        for item in data[
            "recent_predictions"
        ]
    }

    assert levels == {
        "LOW",
        "MEDIUM",
        "HIGH",
        "VERY HIGH",
    }


def test_model_performance_endpoint_reports_final_v2_evidence(
    client,
    db_session,
):
    admin = create_user(
        db_session,
        email="performance.admin@smartpark.com",
        role="admin",
    )

    response = client.get(
        (
            "/api/admin/analytics/"
            "model-performance"
        ),
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["selected_model"] == (
        "XGBoost Regressor"
    )

    assert data["model_version"] == (
        "2.0-tuned"
    )

    assert data["dataset_type"] == (
        "synthetic"
    )

    assert data["development_rows"] == 8000
    assert data["evaluation_rows"] == 2500

    assert data["evaluation_mae"] == 4.7191
    assert data["evaluation_rmse"] == 5.9884
    assert data["evaluation_r2"] == 0.9159

    assert data[
        "best_cross_validation_rmse"
    ] == 6.0172

    assert len(
        data["feature_importance"]
    ) == 9

    assert (
        "do not represent external "
        "real-world validation"
        in data["evaluation_scope"]
    )
