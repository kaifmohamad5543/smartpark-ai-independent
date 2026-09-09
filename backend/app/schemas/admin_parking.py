import uuid
from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdminParkingLocationCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    address: str = Field(
        min_length=5,
        max_length=255
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    postcode: str = Field(
        min_length=3,
        max_length=20
    )

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    initial_spaces: int = Field(
        ge=1,
        le=1000
    )

    hourly_rate: float = Field(
        ge=0,
        le=1000
    )

    opening_time: time | None = None
    closing_time: time | None = None

    is_24_hours: bool = False
    dynamic_pricing_enabled: bool = False
    is_active: bool = True

    @model_validator(mode="after")
    def validate_opening_hours(self):
        if self.is_24_hours:
            return self

        if (
            self.opening_time is None
            or self.closing_time is None
        ):
            raise ValueError(
                "Opening and closing times are required "
                "when the location is not open 24 hours."
            )

        if self.opening_time == self.closing_time:
            raise ValueError(
                "Opening and closing times cannot be identical."
            )

        return self


class AdminParkingLocationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    address: str | None = Field(
        default=None,
        min_length=5,
        max_length=255
    )

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    postcode: str | None = Field(
        default=None,
        min_length=3,
        max_length=20
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    hourly_rate: float | None = Field(
        default=None,
        ge=0,
        le=1000
    )

    opening_time: time | None = None
    closing_time: time | None = None

    is_24_hours: bool | None = None


class ParkingLocationStatusUpdate(BaseModel):
    is_active: bool


class AdminParkingLocationResponse(BaseModel):
    id: uuid.UUID

    name: str
    address: str
    city: str
    postcode: str

    latitude: float
    longitude: float

    total_spaces: int
    hourly_rate: float

    opening_time: time | None
    closing_time: time | None

    is_24_hours: bool
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


ParkingSpaceType = Literal[
    "standard",
    "compact",
    "large"
]


EVChargerStatus = Literal[
    "available",
    "occupied",
    "offline",
    "maintenance"
]


class AdminParkingSpaceCreate(BaseModel):
    space_number: str = Field(
        min_length=1,
        max_length=30
    )

    space_type: ParkingSpaceType = "standard"

    has_ev_charging: bool = False

    ev_charger_status: EVChargerStatus | None = None

    is_accessible: bool = False

    is_available: bool = True
    is_active: bool = True


class AdminParkingSpaceUpdate(BaseModel):
    space_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    space_type: ParkingSpaceType | None = None

    has_ev_charging: bool | None = None

    ev_charger_status: EVChargerStatus | None = None

    is_accessible: bool | None = None

    is_available: bool | None = None
    is_active: bool | None = None


class AdminParkingSpaceResponse(BaseModel):
    id: uuid.UUID
    parking_location_id: uuid.UUID

    space_number: str
    space_type: str

    is_available: bool
    has_ev_charging: bool

    ev_charger_status: str | None
    ev_charger_updated_at: datetime | None

    is_accessible: bool
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )
