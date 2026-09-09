import uuid
from typing import Literal

from pydantic import BaseModel, Field


RecommendationMode = Literal[
    "balanced",
    "closest",
    "cheapest",
    "most_available",
    "low_demand"
]


class RecommendationRequest(BaseModel):
    destination_latitude: float = Field(
        ge=-90,
        le=90
    )

    destination_longitude: float = Field(
        ge=-180,
        le=180
    )

    hour: int = Field(
        ge=0,
        le=23
    )

    day_of_week: int = Field(
        ge=0,
        le=6
    )

    traffic_level: int = Field(
        ge=0,
        le=3
    )

    weather: int = Field(
        ge=0,
        le=3
    )

    event_level: int = Field(
        ge=0,
        le=3
    )

    preference_mode: RecommendationMode = "balanced"


class ScoreBreakdown(BaseModel):
    distance: float
    price: float
    current_availability: float
    current_occupancy: float
    predicted_availability: float
    predicted_occupancy: float
    rating: float


class ParkingRecommendation(BaseModel):
    parking_location_id: uuid.UUID
    parking_name: str

    latitude: float
    longitude: float

    distance_km: float
    hourly_rate: float

    total_spaces: int
    current_available_spaces: int
    current_occupancy: float

    predicted_available_spaces: int
    predicted_occupancy: float
    predicted_availability: float

    rating: float
    review_count: int

    recommendation_score: float
    recommendation_rank: int

    score_breakdown: ScoreBreakdown

    recommendation_reasons: list[str]


class RecommendationResponse(BaseModel):
    destination_latitude: float
    destination_longitude: float

    preference_mode: RecommendationMode

    recommendations: list[ParkingRecommendation]
