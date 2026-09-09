import uuid

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=2, max_length=20)
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    colour: str = Field(min_length=1, max_length=40)
    vehicle_type: str = Field(default="car", min_length=2, max_length=30)
    is_default: bool = False


class VehicleUpdate(BaseModel):
    registration_number: str | None = Field(
        default=None,
        min_length=2,
        max_length=20
    )
    make: str | None = Field(default=None, min_length=1, max_length=60)
    model: str | None = Field(default=None, min_length=1, max_length=60)
    colour: str | None = Field(default=None, min_length=1, max_length=40)
    vehicle_type: str | None = Field(default=None, min_length=2, max_length=30)
    is_default: bool | None = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    registration_number: str
    make: str
    model: str
    colour: str
    vehicle_type: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)
