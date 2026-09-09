import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AdminReservationResponse(BaseModel):
    id: uuid.UUID
    booking_code: str

    user_id: uuid.UUID
    user_name: str
    user_email: str

    vehicle_id: uuid.UUID
    vehicle_registration: str
    vehicle_make: str
    vehicle_model: str

    parking_location_id: uuid.UUID
    parking_location_name: str

    parking_space_id: uuid.UUID
    parking_space_number: str
    parking_space_type: str

    reserved_from: datetime
    reserved_until: datetime

    status: str

    estimated_cost: Decimal
    final_cost: Decimal | None

    checked_in_at: datetime | None
    checked_out_at: datetime | None
    cancelled_at: datetime | None

    created_at: datetime
    updated_at: datetime
