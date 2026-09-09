import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID
    reservation_id: uuid.UUID
    parking_session_id: uuid.UUID | None

    payment_reference: str

    transaction_type: str
    payment_method: str

    amount: Decimal
    status: str

    paid_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class RefundResponse(BaseModel):
    original_payment: PaymentResponse
    refund_payment: PaymentResponse


class AdminPaymentResponse(BaseModel):
    id: uuid.UUID

    user_id: uuid.UUID
    user_name: str
    user_email: str

    reservation_id: uuid.UUID
    parking_session_id: uuid.UUID | None
    related_payment_id: uuid.UUID | None

    payment_reference: str
    transaction_type: str
    payment_method: str

    amount: Decimal
    status: str

    paid_at: datetime | None
    created_at: datetime

    is_refundable: bool
