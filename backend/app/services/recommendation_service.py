from math import atan2, cos, radians, sin, sqrt

from sqlalchemy.orm import Session

from app.ml.predictor_v2 import predictor_v2
from app.schemas.recommendation import RecommendationRequest
from app.services.parking_service import (
    get_active_parking_locations,
    get_parking_availability
)
from app.services.review_service import get_average_rating


NEUTRAL_UNRATED_SCORE = 3.0


WEIGHT_PROFILES = {
    "balanced": {
        "distance": 0.25,
        "price": 0.15,
        "current_availability": 0.15,
        "current_occupancy": 0.10,
        "predicted_availability": 0.15,
        "predicted_occupancy": 0.10,
        "rating": 0.10
    },

    "closest": {
        "distance": 0.50,
        "price": 0.10,
        "current_availability": 0.10,
        "current_occupancy": 0.05,
        "predicted_availability": 0.10,
        "predicted_occupancy": 0.05,
        "rating": 0.10
    },

    "cheapest": {
        "distance": 0.10,
        "price": 0.50,
        "current_availability": 0.10,
        "current_occupancy": 0.05,
        "predicted_availability": 0.10,
        "predicted_occupancy": 0.05,
        "rating": 0.10
    },

    "most_available": {
        "distance": 0.10,
        "price": 0.10,
        "current_availability": 0.30,
        "current_occupancy": 0.10,
        "predicted_availability": 0.25,
        "predicted_occupancy": 0.05,
        "rating": 0.10
    },

    "low_demand": {
        "distance": 0.10,
        "price": 0.10,
        "current_availability": 0.10,
        "current_occupancy": 0.10,
        "predicted_availability": 0.20,
        "predicted_occupancy": 0.30,
        "rating": 0.10
    }
}


def haversine_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float
) -> float:
    earth_radius_km = 6371.0

    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)
    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


def normalize_lower_is_better(
    value: float,
    minimum: float,
    maximum: float
) -> float:
    if maximum == minimum:
        return 1.0

    return 1 - (
        (value - minimum)
        / (maximum - minimum)
    )


def build_recommendation_reasons(
    candidate: dict,
    preference_mode: str
) -> list[str]:
    reasons = []

    if candidate["distance_km"] <= 1:
        reasons.append(
            f"Very close to destination at {candidate['distance_km']} km."
        )
    elif candidate["distance_km"] <= 3:
        reasons.append(
            f"Reasonable distance of {candidate['distance_km']} km."
        )

    availability_ratio = (
        candidate["current_available_spaces"]
        / candidate["total_spaces"]
    )

    if availability_ratio >= 0.60:
        reasons.append(
            f"High current availability with "
            f"{candidate['current_available_spaces']} spaces free."
        )
    elif availability_ratio >= 0.30:
        reasons.append(
            f"Moderate current availability with "
            f"{candidate['current_available_spaces']} spaces free."
        )

    if candidate["predicted_occupancy"] < 50:
        reasons.append(
            f"Low predicted demand at "
            f"{candidate['predicted_occupancy']}% occupancy."
        )
    elif candidate["predicted_occupancy"] < 70:
        reasons.append(
            f"Moderate predicted demand at "
            f"{candidate['predicted_occupancy']}% occupancy."
        )

    if candidate["predicted_availability"] >= 40:
        reasons.append(
            f"Good predicted availability of "
            f"{candidate['predicted_availability']}%."
        )

    if candidate["hourly_rate"] <= 3.50:
        reasons.append(
            f"Low parking price at £"
            f"{candidate['hourly_rate']:.2f}/hour."
        )

    if candidate["review_count"] > 0:
        if candidate["rating"] >= 4:
            reasons.append(
                f"Strong user rating of "
                f"{candidate['rating']:.1f}/5 "
                f"from {candidate['review_count']} review(s)."
            )
        else:
            reasons.append(
                f"User rating of "
                f"{candidate['rating']:.1f}/5 "
                f"from {candidate['review_count']} review(s)."
            )
    else:
        reasons.append(
            "No user reviews yet; a neutral rating score was used."
        )

    mode_reason = {
        "balanced":
            "Selected using a balanced mix of distance, price, demand and availability.",

        "closest":
            "Distance was given the highest priority.",

        "cheapest":
            "Parking price was given the highest priority.",

        "most_available":
            "Current and predicted availability were prioritised.",

        "low_demand":
            "Lower predicted parking demand was prioritised."
    }

    reasons.append(
        mode_reason[preference_mode]
    )

    return reasons


def generate_recommendations(
    db: Session,
    request: RecommendationRequest
) -> list[dict]:

    parking_locations = get_active_parking_locations(db)

    candidates = []

    for location in parking_locations:
        availability = get_parking_availability(
            db=db,
            parking_location=location
        )

        total_spaces = availability["total_spaces"]

        if total_spaces == 0:
            continue

        current_available_spaces = availability[
            "available_spaces"
        ]

        current_occupancy = availability[
            "occupancy_percentage"
        ]

        distance_km = haversine_distance(
            request.destination_latitude,
            request.destination_longitude,
            location.latitude,
            location.longitude
        )

        predicted_occupancy = predictor_v2.predict(
            hour=request.hour,
            day_of_week=request.day_of_week,
            previous_occupancy=current_occupancy,
            current_occupancy=current_occupancy,
            traffic_level=request.traffic_level,
            weather=request.weather,
            event_level=request.event_level,
            parking_price=float(location.hourly_rate),
            total_spaces=total_spaces
        )

        predicted_availability = round(
            max(
                0.0,
                100.0 - predicted_occupancy
            ),
            2
        )

        predicted_available_spaces = round(
            total_spaces
            * predicted_availability
            / 100
        )

        average_rating, review_count = get_average_rating(
            db=db,
            parking_location_id=location.id
        )

        effective_rating = (
            average_rating
            if review_count > 0
            else NEUTRAL_UNRATED_SCORE
        )

        candidates.append(
            {
                "parking_location_id": location.id,
                "parking_name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "distance_km": round(distance_km, 2),
                "hourly_rate": float(location.hourly_rate),
                "total_spaces": total_spaces,
                "current_available_spaces": current_available_spaces,
                "current_occupancy": current_occupancy,
                "predicted_available_spaces": predicted_available_spaces,
                "predicted_occupancy": predicted_occupancy,
                "predicted_availability": predicted_availability,
                "rating": effective_rating,
                "review_count": review_count
            }
        )

    if not candidates:
        return []

    distances = [
        item["distance_km"]
        for item in candidates
    ]

    prices = [
        item["hourly_rate"]
        for item in candidates
    ]

    predicted_spaces = [
        item["predicted_available_spaces"]
        for item in candidates
    ]

    min_distance = min(distances)
    max_distance = max(distances)

    min_price = min(prices)
    max_price = max(prices)

    max_predicted_spaces = max(
        predicted_spaces
    )

    weights = WEIGHT_PROFILES[
        request.preference_mode
    ]

    for candidate in candidates:
        distance_score = normalize_lower_is_better(
            candidate["distance_km"],
            min_distance,
            max_distance
        )

        price_score = normalize_lower_is_better(
            candidate["hourly_rate"],
            min_price,
            max_price
        )

        current_availability_score = (
            candidate["current_available_spaces"]
            / candidate["total_spaces"]
        )

        current_occupancy_score = (
            1
            - candidate["current_occupancy"]
            / 100
        )

        predicted_occupancy_score = (
            1
            - candidate["predicted_occupancy"]
            / 100
        )

        if max_predicted_spaces > 0:
            predicted_availability_score = (
                candidate["predicted_available_spaces"]
                / max_predicted_spaces
            )
        else:
            predicted_availability_score = 0

        rating_score = (
            candidate["rating"] / 5
        )

        score_breakdown = {
            "distance": round(
                distance_score * 100,
                2
            ),

            "price": round(
                price_score * 100,
                2
            ),

            "current_availability": round(
                current_availability_score * 100,
                2
            ),

            "current_occupancy": round(
                current_occupancy_score * 100,
                2
            ),

            "predicted_availability": round(
                predicted_availability_score * 100,
                2
            ),

            "predicted_occupancy": round(
                predicted_occupancy_score * 100,
                2
            ),

            "rating": round(
                rating_score * 100,
                2
            )
        }

        recommendation_score = (
            weights["distance"]
            * distance_score

            + weights["price"]
            * price_score

            + weights["current_availability"]
            * current_availability_score

            + weights["current_occupancy"]
            * current_occupancy_score

            + weights["predicted_availability"]
            * predicted_availability_score

            + weights["predicted_occupancy"]
            * predicted_occupancy_score

            + weights["rating"]
            * rating_score
        )

        candidate["recommendation_score"] = round(
            recommendation_score * 100,
            2
        )

        candidate[
            "score_breakdown"
        ] = score_breakdown

    candidates.sort(
        key=lambda item: item[
            "recommendation_score"
        ],
        reverse=True
    )

    for index, candidate in enumerate(
        candidates,
        start=1
    ):
        candidate["recommendation_rank"] = index

        candidate[
            "recommendation_reasons"
        ] = build_recommendation_reasons(
            candidate,
            request.preference_mode
        )

    return candidates
