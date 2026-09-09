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
from app.schemas.payment import PaymentResponse
from app.services.payment_service import (
    get_user_payment_by_id,
    get_user_payments
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.get(
    "",
    response_model=list[PaymentResponse]
)
def payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_payments(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def payment_details(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = get_user_payment_by_id(
        db=db,
        user_id=current_user.id,
        payment_id=payment_id
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found."
        )

    return payment
