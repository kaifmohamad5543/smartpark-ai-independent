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
from app.schemas.payment import (
    AdminPaymentResponse,
    RefundResponse
)
from app.services.payment_service import (
    get_admin_payments,
    refund_wallet_payment
)
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/api/admin/payments",
    tags=["Admin Payments"]
)


@router.get(
    "",
    response_model=list[AdminPaymentResponse]
)
def list_admin_payments(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_admin_payments(
        db=db
    )


@router.post(
    "/{payment_id}/refund",
    response_model=RefundResponse
)
def refund_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    try:
        original_payment, refund_payment_record = (
            refund_wallet_payment(
                db=db,
                payment_id=payment_id
            )
        )

        return RefundResponse(
            original_payment=original_payment,
            refund_payment=refund_payment_record
        )

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
