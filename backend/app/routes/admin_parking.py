import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_parking import (
    AdminParkingLocationCreate,
    AdminParkingLocationResponse,
    AdminParkingLocationUpdate,
    AdminParkingSpaceCreate,
    AdminParkingSpaceResponse,
    AdminParkingSpaceUpdate,
    ParkingLocationStatusUpdate
)
from app.services.admin_parking_service import (
    create_admin_parking_location,
    create_admin_parking_space,
    get_admin_parking_location_by_id,
    get_admin_parking_space_by_id,
    get_admin_parking_spaces,
    get_all_admin_parking_locations,
    set_parking_location_status,
    update_admin_parking_location,
    update_admin_parking_space
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/parking",
    tags=["Admin Parking Management"]
)


@router.get(
    "/locations",
    response_model=list[AdminParkingLocationResponse]
)
def list_admin_parking_locations(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_all_admin_parking_locations(
        db=db
    )


@router.post(
    "/locations",
    response_model=AdminParkingLocationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_parking_location(
    location_data: AdminParkingLocationCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    try:
        return create_admin_parking_location(
            db=db,
            location_data=location_data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.patch(
    "/locations/{parking_location_id}",
    response_model=AdminParkingLocationResponse
)
def update_parking_location(
    parking_location_id: uuid.UUID,
    location_data: AdminParkingLocationUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    location = get_admin_parking_location_by_id(
        db=db,
        parking_location_id=parking_location_id
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    try:
        return update_admin_parking_location(
            db=db,
            location=location,
            location_data=location_data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.patch(
    "/locations/{parking_location_id}/status",
    response_model=AdminParkingLocationResponse
)
def update_parking_location_status(
    parking_location_id: uuid.UUID,
    status_data: ParkingLocationStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    location = get_admin_parking_location_by_id(
        db=db,
        parking_location_id=parking_location_id
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    try:
        return set_parking_location_status(
            db=db,
            location=location,
            is_active=status_data.is_active
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.get(
    "/locations/{parking_location_id}/spaces",
    response_model=list[AdminParkingSpaceResponse]
)
def list_admin_parking_spaces(
    parking_location_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    location = get_admin_parking_location_by_id(
        db=db,
        parking_location_id=parking_location_id
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    return get_admin_parking_spaces(
        db=db,
        parking_location_id=parking_location_id
    )


@router.post(
    "/locations/{parking_location_id}/spaces",
    response_model=AdminParkingSpaceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_parking_space(
    parking_location_id: uuid.UUID,
    space_data: AdminParkingSpaceCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    location = get_admin_parking_location_by_id(
        db=db,
        parking_location_id=parking_location_id
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking location not found."
        )

    try:
        return create_admin_parking_space(
            db=db,
            parking_location=location,
            space_data=space_data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.patch(
    "/spaces/{parking_space_id}",
    response_model=AdminParkingSpaceResponse
)
def update_parking_space(
    parking_space_id: uuid.UUID,
    space_data: AdminParkingSpaceUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    parking_space = get_admin_parking_space_by_id(
        db=db,
        parking_space_id=parking_space_id
    )

    if parking_space is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking space not found."
        )

    try:
        return update_admin_parking_space(
            db=db,
            parking_space=parking_space,
            space_data=space_data
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )
