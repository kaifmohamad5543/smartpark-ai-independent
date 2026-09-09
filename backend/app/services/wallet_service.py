import secrets
import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction


MONEY_QUANTIZER = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP
    )


def generate_wallet_transaction_reference(
    db: Session
) -> str:

    for _ in range(20):
        reference = (
            "WLT-"
            + secrets.token_hex(6).upper()
        )

        existing = db.scalar(
            select(WalletTransaction).where(
                WalletTransaction.transaction_reference
                == reference
            )
        )

        if existing is None:
            return reference

    raise RuntimeError(
        "Unable to generate wallet transaction reference."
    )


def get_or_create_wallet(
    db: Session,
    user_id: uuid.UUID
) -> Wallet:

    wallet = db.scalar(
        select(Wallet).where(
            Wallet.user_id == user_id
        )
    )

    if wallet:
        return wallet

    wallet = Wallet(
        user_id=user_id,
        balance=Decimal("0.00")
    )

    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet


def top_up_wallet(
    db: Session,
    user_id: uuid.UUID,
    amount: Decimal
) -> tuple[Wallet, WalletTransaction]:

    amount = money(amount)

    wallet = db.scalar(
        select(Wallet)
        .where(
            Wallet.user_id == user_id
        )
        .with_for_update()
    )

    if wallet is None:
        wallet = Wallet(
            user_id=user_id,
            balance=Decimal("0.00")
        )

        db.add(wallet)
        db.flush()

    balance_before = money(
        wallet.balance
    )

    balance_after = money(
        balance_before + amount
    )

    wallet.balance = balance_after

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=user_id,
        reservation_id=None,
        payment_id=None,
        transaction_reference=(
            generate_wallet_transaction_reference(db)
        ),
        transaction_type="top_up",
        direction="credit",
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        description="SmartPark wallet top-up."
    )

    db.add(transaction)

    db.commit()

    db.refresh(wallet)
    db.refresh(transaction)

    return wallet, transaction


def get_wallet_transactions(
    db: Session,
    user_id: uuid.UUID
) -> list[WalletTransaction]:

    statement = (
        select(WalletTransaction)
        .where(
            WalletTransaction.user_id == user_id
        )
        .order_by(
            WalletTransaction.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def debit_wallet_for_payment(
    db: Session,
    user_id: uuid.UUID,
    amount: Decimal,
    reservation_id: uuid.UUID,
    payment_id: uuid.UUID
) -> WalletTransaction | None:

    amount = money(amount)

    # No ledger debit is necessary for a zero-value charge.
    if amount <= Decimal("0.00"):
        return None

    wallet = db.scalar(
        select(Wallet)
        .where(
            Wallet.user_id == user_id
        )
        .with_for_update()
    )

    if wallet is None:
        raise ValueError(
            "Wallet not found. Please top up your wallet first."
        )

    balance_before = money(
        wallet.balance
    )

    if balance_before < amount:
        raise ValueError(
            f"Insufficient wallet balance. "
            f"Required £{amount:.2f}, "
            f"available £{balance_before:.2f}."
        )

    balance_after = money(
        balance_before - amount
    )

    wallet.balance = balance_after

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=user_id,
        reservation_id=reservation_id,
        payment_id=payment_id,
        transaction_reference=(
            generate_wallet_transaction_reference(db)
        ),
        transaction_type="parking_payment",
        direction="debit",
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        description="Parking charge paid using SmartPark wallet."
    )

    db.add(transaction)
    db.flush()

    return transaction
