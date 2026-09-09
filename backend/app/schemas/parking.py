import uuid
from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class ParkingLocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    address: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    postcode: str = Field(min_length=3, max_length=20)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    total_spaces: int = Field(gt=0)
    hourly_rate: float = Field(ge=0)

    opening_time: time | None = None
    closing_time: time | None = None

    is_24_hours: bool = False
    dynamic_pricing_enabled: bool = False
    is_active: bool = True


class ParkingLocationResponse(BaseModel):
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
    dynamic_pricing_enabled: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ParkingAvailabilityResponse(BaseModel):
    parking_location_id: uuid.UUID
    parking_name: str
    total_spaces: int
    available_spaces: int
    occupied_spaces: int
    occupancy_percentage: float

    total_ev_chargers: int
    available_ev_chargers: int
    occupied_ev_chargers: int
    offline_ev_chargers: int
    maintenance_ev_chargers: int
