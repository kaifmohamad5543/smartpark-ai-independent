import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    parking_location_id: uuid.UUID

    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str | None = Field(
        default=None,
        max_length=1000
    )


class ReviewResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parking_location_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ParkingRatingSummary(BaseModel):
    parking_location_id: uuid.UUID
    average_rating: float
    review_count: int
