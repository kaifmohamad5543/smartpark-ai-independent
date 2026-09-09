import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PredictionCreate(BaseModel):
    parking_location_id: uuid.UUID

    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)

    previous_occupancy: float = Field(
        ge=0,
        le=100
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


class PredictionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parking_location_id: uuid.UUID

    hour: int
    day_of_week: int
    previous_occupancy: float
    current_occupancy: float | None = None

    traffic_level: int
    weather: int
    event_level: int

    parking_price: Decimal
    available_spaces: int
    total_spaces: int | None = None
    model_version: str | None = None

    predicted_occupancy: float
    predicted_availability: float

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class FeatureImportanceItem(BaseModel):
    feature: str
    display_name: str
    importance: float
    importance_percentage: float


class FeatureImportanceResponse(BaseModel):
    model_name: str
    explanation_type: str
    features: list[FeatureImportanceItem]
