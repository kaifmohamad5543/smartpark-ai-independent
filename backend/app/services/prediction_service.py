import uuid

from sqlalchemy.orm import Session

from app.ml.predictor_v2 import predictor_v2
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate
from app.services.parking_service import (
    get_parking_availability,
    get_parking_location_by_id
)


def create_prediction(
    db: Session,
    user_id: uuid.UUID,
    prediction_data: PredictionCreate
) -> Prediction:

    parking_location = get_parking_location_by_id(
        db=db,
        parking_location_id=prediction_data.parking_location_id
    )

    if not parking_location:
        raise ValueError(
            "Parking location not found."
        )

    availability = get_parking_availability(
        db=db,
        parking_location=parking_location
    )

    total_spaces = availability[
        "total_spaces"
    ]

    if total_spaces <= 0:
        raise ValueError(
            "Parking location has no active parking spaces."
        )

    current_available_spaces = availability[
        "available_spaces"
    ]

    current_occupancy = availability[
        "occupancy_percentage"
    ]

    parking_price = float(
        parking_location.hourly_rate
    )

    predicted_occupancy = predictor_v2.predict(
        hour=prediction_data.hour,
        day_of_week=prediction_data.day_of_week,
        previous_occupancy=prediction_data.previous_occupancy,
        current_occupancy=current_occupancy,
        traffic_level=prediction_data.traffic_level,
        weather=prediction_data.weather,
        event_level=prediction_data.event_level,
        parking_price=parking_price,
        total_spaces=total_spaces
    )

    predicted_availability = round(
        max(
            0.0,
            100.0 - predicted_occupancy
        ),
        2
    )

    prediction = Prediction(
        user_id=user_id,
        parking_location_id=parking_location.id,
        hour=prediction_data.hour,
        day_of_week=prediction_data.day_of_week,
        previous_occupancy=prediction_data.previous_occupancy,
        current_occupancy=current_occupancy,
        traffic_level=prediction_data.traffic_level,
        weather=prediction_data.weather,
        event_level=prediction_data.event_level,
        parking_price=parking_location.hourly_rate,
        available_spaces=current_available_spaces,
        total_spaces=total_spaces,
        model_version=predictor_v2.model_version,
        predicted_occupancy=predicted_occupancy,
        predicted_availability=predicted_availability
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


from sqlalchemy import select


def get_user_predictions(
    db: Session,
    user_id: uuid.UUID
) -> list[Prediction]:

    statement = (
        select(Prediction)
        .where(
            Prediction.user_id == user_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


import json
from pathlib import Path


FEATURE_IMPORTANCE_PATH = Path(
    "data/processed/feature_importance_v2.json"
)


def get_feature_importance() -> list[dict]:
    if not FEATURE_IMPORTANCE_PATH.exists():
        raise FileNotFoundError(
            "Feature importance results have not been generated."
        )

    with open(
        FEATURE_IMPORTANCE_PATH,
        "r"
    ) as file:
        data = json.load(file)

    features = data.get(
        "features"
    )

    if not isinstance(
        features,
        list
    ):
        raise ValueError(
            "Invalid ML Version 2 feature importance file."
        )

    return features
