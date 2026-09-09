from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin_reservation import (
    AdminReservationResponse,
)
from app.services.admin_reservation_service import (
    get_admin_reservations,
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/reservations",
    tags=["Admin Reservation Management"]
)


@router.get(
    "",
    response_model=list[AdminReservationResponse]
)
def list_admin_reservations(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_admin_reservations(
        db=db
    )
