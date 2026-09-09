import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WalletResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class WalletTopUpRequest(BaseModel):
    amount: Decimal = Field(
        gt=0,
        le=1000,
        decimal_places=2
    )


class WalletTransactionResponse(BaseModel):
    id: uuid.UUID
    wallet_id: uuid.UUID
    user_id: uuid.UUID

    reservation_id: uuid.UUID | None
    payment_id: uuid.UUID | None

    transaction_reference: str
    transaction_type: str
    direction: str

    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal

    description: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class WalletTopUpResponse(BaseModel):
    wallet: WalletResponse
    transaction: WalletTransactionResponse
