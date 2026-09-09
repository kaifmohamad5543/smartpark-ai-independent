import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate
)
from app.services.vehicle_service import (
    create_vehicle,
    get_user_vehicle_by_id,
    get_user_vehicles,
    update_vehicle
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/vehicles",
    tags=["Vehicles"]
)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED
)
def add_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_vehicle(
        db=db,
        user_id=current_user.id,
        vehicle_data=vehicle_data
    )


@router.get(
    "",
    response_model=list[VehicleResponse]
)
def list_my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_vehicles(
        db=db,
        user_id=current_user.id
    )


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse
)
def edit_vehicle(
    vehicle_id: uuid.UUID,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicle = get_user_vehicle_by_id(
        db=db,
        user_id=current_user.id,
        vehicle_id=vehicle_id
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found."
        )

    return update_vehicle(
        db=db,
        vehicle=vehicle,
        vehicle_data=vehicle_data
    )


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.vehicle_service import delete_vehicle

    vehicle = get_user_vehicle_by_id(
        db=db,
        user_id=current_user.id,
        vehicle_id=vehicle_id
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found."
        )

    delete_vehicle(
        db=db,
        vehicle=vehicle
    )

    return None
