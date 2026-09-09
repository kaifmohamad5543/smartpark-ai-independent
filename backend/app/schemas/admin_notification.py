import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AdminNotificationResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID
    user_name: str
    user_email: str

    reservation_id: uuid.UUID | None
    booking_code: str | None

    notification_type: str
    title: str
    message: str

    is_read: bool
    created_at: datetime
    read_at: datetime | None


class AdminNotificationSendRequest(BaseModel):
    recipient_mode: Literal[
        "all_active",
        "single_user",
    ]

    user_id: uuid.UUID | None = None

    title: str = Field(
        min_length=2,
        max_length=150,
    )

    message: str = Field(
        min_length=2,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_recipient(self):
        if (
            self.recipient_mode == "single_user"
            and self.user_id is None
        ):
            raise ValueError(
                "user_id is required for a single-user notification."
            )

        return self


class AdminNotificationSendResponse(BaseModel):
    created_count: int
    message: str
