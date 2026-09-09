from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.parking_session import (
    ParkingSessionHistoryResponse
)
from app.services.parking_session_service import (
    get_user_parking_history
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/parking-sessions",
    tags=["Parking History"]
)


@router.get(
    "",
    response_model=list[ParkingSessionHistoryResponse]
)
def parking_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_parking_history(
        db=db,
        user_id=current_user.id
    )
