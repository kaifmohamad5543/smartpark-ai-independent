import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ParkingSessionHistoryResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID

    booking_code: str

    parking_location_id: uuid.UUID
    parking_name: str

    parking_space_id: uuid.UUID
    space_number: str

    started_at: datetime
    ended_at: datetime | None

    duration_minutes: int | None
    final_cost: Decimal | None

    status: str
    created_at: datetime
