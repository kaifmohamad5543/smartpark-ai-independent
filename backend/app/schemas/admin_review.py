import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminReviewResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID
    user_name: str
    user_email: str

    parking_location_id: uuid.UUID
    parking_location_name: str

    rating: int
    comment: str | None

    created_at: datetime
    updated_at: datetime


class AdminReviewDeleteResponse(BaseModel):
    deleted_review_id: uuid.UUID
    message: str
