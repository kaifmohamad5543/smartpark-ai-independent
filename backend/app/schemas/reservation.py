import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationCreate(BaseModel):
    vehicle_id: uuid.UUID
    parking_location_id: uuid.UUID

    reserved_from: datetime
    reserved_until: datetime

    @model_validator(mode="after")
    def validate_reservation_times(self):
        if self.reserved_until <= self.reserved_from:
            raise ValueError(
                "reserved_until must be later than reserved_from"
            )

        return self


class ReservationResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID
    vehicle_id: uuid.UUID

    parking_location_id: uuid.UUID
    parking_space_id: uuid.UUID

    booking_code: str

    reserved_from: datetime
    reserved_until: datetime

    status: str

    estimated_cost: Decimal

    base_hourly_rate: Decimal | None = None
    applied_hourly_rate: Decimal | None = None
    pricing_multiplier: Decimal | None = None

    current_occupancy_at_booking: (
        Decimal | None
    ) = None

    predicted_occupancy_at_booking: (
        Decimal | None
    ) = None

    pricing_model_version: str | None = None

    checked_in_at: datetime | None
    checked_out_at: datetime | None
    cancelled_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ReservationCancelResponse(BaseModel):
    id: uuid.UUID
    booking_code: str
    status: str
    cancelled_at: datetime


class CheckInRequest(BaseModel):
    booking_code: str = Field(
        min_length=5,
        max_length=20
    )


class CheckOutResponse(BaseModel):
    reservation_id: uuid.UUID
    booking_code: str
    status: str
    checked_in_at: datetime
    checked_out_at: datetime
    final_cost: Decimal

    payment_method: str
    payment_reference: str


class CheckInResponse(BaseModel):
    reservation_id: uuid.UUID
    booking_code: str
    parking_space_id: uuid.UUID
    status: str
    checked_in_at: datetime


from typing import Literal


class CheckOutRequest(BaseModel):
    payment_method: Literal[
        "card",
        "wallet"
    ] = "card"
