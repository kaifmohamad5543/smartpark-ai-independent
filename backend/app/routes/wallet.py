from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.wallet import (
    WalletResponse,
    WalletTopUpRequest,
    WalletTopUpResponse,
    WalletTransactionResponse
)
from app.services.wallet_service import (
    get_or_create_wallet,
    get_wallet_transactions,
    top_up_wallet
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/wallet",
    tags=["Digital Wallet"]
)


@router.get(
    "",
    response_model=WalletResponse
)
def wallet_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_or_create_wallet(
        db=db,
        user_id=current_user.id
    )


@router.post(
    "/top-up",
    response_model=WalletTopUpResponse
)
def wallet_top_up(
    request: WalletTopUpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet, transaction = top_up_wallet(
        db=db,
        user_id=current_user.id,
        amount=request.amount
    )

    return WalletTopUpResponse(
        wallet=wallet,
        transaction=transaction
    )


@router.get(
    "/transactions",
    response_model=list[WalletTransactionResponse]
)
def wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_wallet_transactions(
        db=db,
        user_id=current_user.id
    )
