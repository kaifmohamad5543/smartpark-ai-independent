from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExternalParkingBayResponse(BaseModel):
    source_identifier: str
    restriction_type: str
    parking_spaces: int | None
    times_of_operation: str | None
    maximum_stay: str | None
    tariff: str | None
    road_name: str
    postcode: str | None
    controlled_parking_zone: str | None
    longitude: float
    latitude: float
    spatial_accuracy: str | None
    source_last_uploaded: datetime | None
    source_dataset: str
    source_organisation: str
    source_url: str

    model_config = ConfigDict(
        from_attributes=True
    )


class ExternalParkingBayStatsResponse(BaseModel):
    total_records: int
    declared_parking_spaces: int
    distinct_roads: int
    paid_for_records: int
    ev_charging_records: int
    disabled_bay_records: int
    source_dataset: str
    source_organisation: str
    data_type: str
