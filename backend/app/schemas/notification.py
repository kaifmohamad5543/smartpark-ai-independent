import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    reservation_id: uuid.UUID | None

    notification_type: str
    title: str
    message: str

    is_read: bool

    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class UnreadNotificationCount(BaseModel):
    unread_count: int


class MarkAllReadResponse(BaseModel):
    updated_count: int
    message: str
