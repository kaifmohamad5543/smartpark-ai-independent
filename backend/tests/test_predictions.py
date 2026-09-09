import uuid
from decimal import Decimal

from sqlalchemy import select

from app.ml.features import FEATURE_COLUMNS
from app.ml.predictor_v2 import predictor_v2
from app.models.parking_location import ParkingLocation
from app.models.parking_space import ParkingSpace
from app.models.prediction import Prediction
from app.models.user import User
from app.utils.security import create_access_token, hash_password


def create_user(
    db_session,
    *,
    email="prediction.test@smartpark.com",
):
    user = User(
        full_name="Prediction Test User",
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


def create_location(
    db_session,
    *,
    name="ML V2 Test Parking",
):
    location = ParkingLocation(
        name=name,
        address="40 Prediction Road",
        city="London",
        postcode="E1 5AB",
        latitude=51.518,
        longitude=-0.073,
        total_spaces=12,
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


def create_spaces(
    db_session,
    location,
    *,
    total=12,
    occupied=3,
):
    for index in range(1, total + 1):
        space = ParkingSpace(
            parking_location_id=location.id,
            space_number=f"A{index}",
            space_type="standard",
            is_available=index > occupied,
            has_ev_charging=False,
            is_accessible=False,
            is_active=True,
        )

        db_session.add(space)

    db_session.commit()


def prediction_payload(location):
    return {
        "parking_location_id": str(location.id),
        "hour": 17,
        "day_of_week": 4,
        "previous_occupancy": 25.0,
        "traffic_level": 3,
        "weather": 1,
        "event_level": 2,
    }


def test_prediction_endpoint_requires_authentication(
    client,
    db_session,
):
    location = create_location(db_session)
    create_spaces(
        db_session,
        location,
    )

    response = client.post(
        "/api/predictions",
        json=prediction_payload(location),
    )

    assert response.status_code in {
        401,
        403,
    }


def test_prediction_matches_direct_v2_model_and_is_persisted(
    client,
    db_session,
):
    user = create_user(db_session)

    location = create_location(
        db_session
    )

    create_spaces(
        db_session,
        location,
        total=12,
        occupied=3,
    )

    expected_prediction = predictor_v2.predict(
        hour=17,
        day_of_week=4,
        previous_occupancy=25.0,
        current_occupancy=25.0,
        traffic_level=3,
        weather=1,
        event_level=2,
        parking_price=4.50,
        total_spaces=12,
    )

    response = client.post(
        "/api/predictions",
        json=prediction_payload(location),
        headers=auth_headers(user),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == str(user.id)

    assert data[
        "parking_location_id"
    ] == str(location.id)

    assert data["available_spaces"] == 9
    assert data["current_occupancy"] == 25.0
    assert data["total_spaces"] == 12
    assert data["model_version"] == (
        predictor_v2.model_version
    )

    assert Decimal(
        str(data["parking_price"])
    ) == Decimal("4.50")

    assert data[
        "predicted_occupancy"
    ] == expected_prediction

    assert data[
        "predicted_availability"
    ] == round(
        100.0 - expected_prediction,
        2,
    )

    prediction = db_session.get(
        Prediction,
        data["id"],
    )

    assert prediction is not None

    assert prediction.user_id == user.id

    assert prediction.predicted_occupancy == (
        expected_prediction
    )

    assert prediction.available_spaces == 9
    assert prediction.current_occupancy == 25.0
    assert prediction.total_spaces == 12
    assert prediction.model_version == (
        predictor_v2.model_version
    )


def test_prediction_rejects_unknown_location(
    client,
    db_session,
):
    user = create_user(db_session)

    payload = {
        "parking_location_id": str(
            uuid.uuid4()
        ),
        "hour": 17,
        "day_of_week": 4,
        "previous_occupancy": 25.0,
        "traffic_level": 3,
        "weather": 1,
        "event_level": 2,
    }

    response = client.post(
        "/api/predictions",
        json=payload,
        headers=auth_headers(user),
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Parking location not found."
    )


def test_prediction_rejects_location_without_active_spaces(
    client,
    db_session,
):
    user = create_user(db_session)

    location = create_location(
        db_session,
        name="Empty ML Parking",
    )

    response = client.post(
        "/api/predictions",
        json=prediction_payload(location),
        headers=auth_headers(user),
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Parking location has no active "
        "parking spaces."
    )


def test_prediction_history_is_user_specific(
    client,
    db_session,
):
    user_one = create_user(
        db_session,
        email="prediction.one@smartpark.com",
    )

    user_two = create_user(
        db_session,
        email="prediction.two@smartpark.com",
    )

    location = create_location(
        db_session
    )

    create_spaces(
        db_session,
        location,
    )

    first = client.post(
        "/api/predictions",
        json=prediction_payload(location),
        headers=auth_headers(user_one),
    )

    second = client.post(
        "/api/predictions",
        json=prediction_payload(location),
        headers=auth_headers(user_two),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(
        "/api/predictions",
        headers=auth_headers(user_one),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == (
        first.json()["id"]
    )

    assert data[0]["user_id"] == str(
        user_one.id
    )

    stored = db_session.scalars(
        select(Prediction).where(
            Prediction.user_id
            == user_one.id
        )
    ).all()

    assert len(stored) == 1


def test_feature_importance_and_model_metadata_are_v2(
    client,
    db_session,
):
    user = create_user(db_session)

    response = client.get(
        "/api/predictions/feature-importance",
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["model_name"] == (
        "SmartPark XGBoost V2 Tuned"
    )

    assert data["explanation_type"] == (
        "Global Model-Native "
        "Feature Importance"
    )

    features = data["features"]

    assert len(features) == 9

    assert features[0]["feature"] == (
        "current_occupancy"
    )

    assert features[0][
        "importance_percentage"
    ] == 46.41

    feature_names = {
        item["feature"]
        for item in features
    }

    assert "parking_location" not in (
        feature_names
    )

    assert "available_spaces" not in (
        feature_names
    )

    assert predictor_v2.model_version == (
        "2.0-tuned"
    )

    assert predictor_v2.feature_columns == (
        FEATURE_COLUMNS
    )

    assert "parking_location" not in (
        FEATURE_COLUMNS
    )

    assert "available_spaces" not in (
        FEATURE_COLUMNS
    )
