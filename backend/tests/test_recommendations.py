from decimal import Decimal

from app.ml.predictor_v2 import predictor_v2
from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.user import User
from app.utils.security import create_access_token, hash_password


def create_user(db_session):
    user = User(
        full_name="Recommendation Test User",
        email="recommendation.test@smartpark.com",
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


def create_location(
    db_session,
    *,
    name,
    latitude,
    longitude,
    hourly_rate,
    active=True,
):
    location = ParkingLocation(
        name=name,
        address=f"{name} Road",
        city="London",
        postcode="E1 6AB",
        latitude=latitude,
        longitude=longitude,
        total_spaces=10,
        hourly_rate=Decimal(hourly_rate),
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
    total=10,
    occupied=2,
    active=True,
):
    for index in range(1, total + 1):
        space = ParkingSpace(
            parking_location_id=location.id,
            space_number=f"S{index}",
            space_type="standard",
            is_available=index > occupied,
            has_ev_charging=False,
            is_accessible=False,
            is_active=active,
        )

        db_session.add(space)

    db_session.commit()


def request_payload(
    *,
    mode="balanced",
):
    return {
        "destination_latitude": 51.5175,
        "destination_longitude": -0.0826,
        "hour": 17,
        "day_of_week": 4,
        "traffic_level": 3,
        "weather": 1,
        "event_level": 2,
        "preference_mode": mode,
    }


def test_recommendation_endpoint_requires_authentication(
    client,
):
    response = client.post(
        "/api/recommendations",
        json=request_payload(),
    )

    assert response.status_code in {
        401,
        403,
    }


def test_balanced_recommendations_use_v2_prediction_and_rank_results(
    client,
    db_session,
):
    user = create_user(db_session)

    first = create_location(
        db_session,
        name="Recommendation Alpha",
        latitude=51.5176,
        longitude=-0.0827,
        hourly_rate="4.50",
    )

    second = create_location(
        db_session,
        name="Recommendation Beta",
        latitude=51.5300,
        longitude=-0.0900,
        hourly_rate="3.50",
    )

    create_spaces(
        db_session,
        first,
        total=10,
        occupied=2,
    )

    create_spaces(
        db_session,
        second,
        total=10,
        occupied=2,
    )

    response = client.post(
        "/api/recommendations",
        json=request_payload(
            mode="balanced"
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["preference_mode"] == (
        "balanced"
    )

    recommendations = data[
        "recommendations"
    ]

    assert len(recommendations) == 2

    assert [
        item["recommendation_rank"]
        for item in recommendations
    ] == [1, 2]

    assert recommendations[0][
        "recommendation_score"
    ] >= recommendations[1][
        "recommendation_score"
    ]

    for item in recommendations:
        assert 0 <= (
            item["predicted_occupancy"]
        ) <= 100

        assert 0 <= (
            item["predicted_availability"]
        ) <= 100

        assert item[
            "predicted_availability"
        ] == round(
            100
            - item["predicted_occupancy"],
            2,
        )

        assert len(
            item["recommendation_reasons"]
        ) >= 1

        assert item["rating"] == 3.0
        assert item["review_count"] == 0

    alpha = next(
        item
        for item in recommendations
        if item["parking_location_id"]
        == str(first.id)
    )

    expected = predictor_v2.predict(
        hour=17,
        day_of_week=4,
        previous_occupancy=20.0,
        current_occupancy=20.0,
        traffic_level=3,
        weather=1,
        event_level=2,
        parking_price=4.50,
        total_spaces=10,
    )

    assert alpha[
        "predicted_occupancy"
    ] == expected

    assert predictor_v2.model_version == (
        "2.0-tuned"
    )


def test_closest_mode_prioritises_nearest_identical_location(
    client,
    db_session,
):
    user = create_user(db_session)

    near = create_location(
        db_session,
        name="Nearest Parking",
        latitude=51.5176,
        longitude=-0.0826,
        hourly_rate="4.00",
    )

    far = create_location(
        db_session,
        name="Farther Parking",
        latitude=51.5600,
        longitude=-0.1200,
        hourly_rate="4.00",
    )

    create_spaces(
        db_session,
        near,
        total=10,
        occupied=2,
    )

    create_spaces(
        db_session,
        far,
        total=10,
        occupied=2,
    )

    response = client.post(
        "/api/recommendations",
        json=request_payload(
            mode="closest"
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    recommendations = response.json()[
        "recommendations"
    ]

    assert recommendations[0][
        "parking_location_id"
    ] == str(near.id)

    assert recommendations[0][
        "distance_km"
    ] < recommendations[1][
        "distance_km"
    ]

    assert (
        "Distance was given the highest priority."
        in recommendations[0][
            "recommendation_reasons"
        ]
    )


def test_cheapest_mode_prioritises_cheaper_identical_location(
    client,
    db_session,
):
    user = create_user(db_session)

    expensive = create_location(
        db_session,
        name="Expensive Parking",
        latitude=51.5200,
        longitude=-0.0850,
        hourly_rate="7.00",
    )

    cheap = create_location(
        db_session,
        name="Cheap Parking",
        latitude=51.5200,
        longitude=-0.0850,
        hourly_rate="2.00",
    )

    create_spaces(
        db_session,
        expensive,
        total=10,
        occupied=2,
    )

    create_spaces(
        db_session,
        cheap,
        total=10,
        occupied=2,
    )

    response = client.post(
        "/api/recommendations",
        json=request_payload(
            mode="cheapest"
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    recommendations = response.json()[
        "recommendations"
    ]

    assert recommendations[0][
        "parking_location_id"
    ] == str(cheap.id)

    assert recommendations[0][
        "hourly_rate"
    ] == 2.0

    assert (
        "Parking price was given the highest priority."
        in recommendations[0][
            "recommendation_reasons"
        ]
    )


def test_dynamic_active_location_is_included_and_zero_space_location_skipped(
    client,
    db_session,
):
    user = create_user(db_session)

    dynamic = create_location(
        db_session,
        name="Dynamic Admin Location",
        latitude=51.5148,
        longitude=-0.0610,
        hourly_rate="3.75",
    )

    create_spaces(
        db_session,
        dynamic,
        total=12,
        occupied=3,
    )

    empty = create_location(
        db_session,
        name="Empty Dynamic Location",
        latitude=51.5100,
        longitude=-0.0600,
        hourly_rate="2.50",
    )

    response = client.post(
        "/api/recommendations",
        json=request_payload(),
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    recommendations = response.json()[
        "recommendations"
    ]

    ids = {
        item["parking_location_id"]
        for item in recommendations
    }

    assert str(dynamic.id) in ids
    assert str(empty.id) not in ids

    dynamic_result = next(
        item
        for item in recommendations
        if item["parking_location_id"]
        == str(dynamic.id)
    )

    assert dynamic_result[
        "total_spaces"
    ] == 12

    assert dynamic_result[
        "current_available_spaces"
    ] == 9

    assert dynamic_result[
        "current_occupancy"
    ] == 25.0

    assert dynamic_result[
        "predicted_available_spaces"
    ] >= 0
