import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.parking import (
    ParkingAvailabilityResponse,
    ParkingLocationResponse
)
from app.services.parking_service import (
    get_active_parking_locations,
    get_parking_availability,
    get_parking_location_by_id
)


router = APIRouter(
    prefix="/api/parking",
    tags=["Parking"]
)


@router.get(
    "/locations",
    response_model=list[ParkingLocationResponse]
)
def list_parking_locations(
    db: Session = Depends(get_db)
):
    return get_active_parking_locations(db)


@router.get(
    "/locations/{parking_location_id}",
    response_model=ParkingLocationResponse
)
def get_parking_location(
    parking_location_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    parking_location = get_parking_location_by_id(
        db,
        parking_location_id
    )

    if not parking_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    return parking_location


@router.get(
    "/locations/{parking_location_id}/availability",
    response_model=ParkingAvailabilityResponse
)
def parking_availability(
    parking_location_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    parking_location = get_parking_location_by_id(
        db,
        parking_location_id
    )

    if not parking_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    return get_parking_availability(
        db,
        parking_location
    )
