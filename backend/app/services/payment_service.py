import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parking_session import ParkingSession
from app.models.payment import Payment
from app.models.reservation import Reservation


def generate_unique_payment_reference(
    db: Session
) -> str:

    for _ in range(20):
        reference = (
            "PAY-"
            + secrets.token_hex(6).upper()
        )

        existing = db.scalar(
            select(Payment).where(
                Payment.payment_reference
                == reference
            )
        )

        if existing is None:
            return reference

    raise RuntimeError(
        "Unable to generate a unique payment reference."
    )


def get_payment_by_reservation(
    db: Session,
    reservation_id: uuid.UUID
) -> Payment | None:

    return db.scalar(
        select(Payment).where(
            Payment.reservation_id
            == reservation_id,
            Payment.transaction_type
            == "parking_charge"
        )
    )


def create_checkout_payment(
    db: Session,
    reservation: Reservation,
    parking_session: ParkingSession,
    amount: Decimal,
    payment_method: str = "card"
) -> Payment:

    existing = get_payment_by_reservation(
        db=db,
        reservation_id=reservation.id
    )

    if existing:
        return existing

    payment = Payment(
        user_id=reservation.user_id,
        reservation_id=reservation.id,
        parking_session_id=parking_session.id,
        payment_reference=(
            generate_unique_payment_reference(db)
        ),
        transaction_type="parking_charge",
        payment_method=payment_method,
        amount=amount,
        status="paid",
        paid_at=datetime.now(timezone.utc)
    )

    db.add(payment)
    db.flush()

    return payment


def get_user_payments(
    db: Session,
    user_id: uuid.UUID
) -> list[Payment]:

    statement = (
        select(Payment)
        .where(
            Payment.user_id == user_id
        )
        .order_by(
            Payment.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_user_payment_by_id(
    db: Session,
    user_id: uuid.UUID,
    payment_id: uuid.UUID
) -> Payment | None:

    statement = select(Payment).where(
        Payment.id == payment_id,
        Payment.user_id == user_id
    )

    return db.scalar(statement)


from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.services.wallet_service import (
    generate_wallet_transaction_reference,
    money
)


def refund_wallet_payment(
    db: Session,
    payment_id: uuid.UUID
) -> tuple[Payment, Payment]:

    original_payment = db.scalar(
        select(Payment)
        .where(
            Payment.id == payment_id
        )
        .with_for_update()
    )

    if original_payment is None:
        raise ValueError(
            "Original payment not found."
        )

    if original_payment.transaction_type != "parking_charge":
        raise ValueError(
            "Only parking charge payments can be refunded."
        )

    if original_payment.payment_method != "wallet":
        raise ValueError(
            "Only wallet payments are supported by this refund flow."
        )

    if original_payment.status == "refunded":
        raise ValueError(
            "This payment has already been refunded."
        )

    existing_refund = db.scalar(
        select(Payment).where(
            Payment.related_payment_id
            == original_payment.id,
            Payment.transaction_type
            == "refund"
        )
    )

    if existing_refund:
        raise ValueError(
            "A refund already exists for this payment."
        )

    wallet = db.scalar(
        select(Wallet)
        .where(
            Wallet.user_id
            == original_payment.user_id
        )
        .with_for_update()
    )

    if wallet is None:
        raise ValueError(
            "User wallet was not found."
        )

    refund_amount = money(
        original_payment.amount
    )

    balance_before = money(
        wallet.balance
    )

    balance_after = money(
        balance_before + refund_amount
    )

    refund_payment = Payment(
        user_id=original_payment.user_id,
        reservation_id=original_payment.reservation_id,
        parking_session_id=(
            original_payment.parking_session_id
        ),
        related_payment_id=original_payment.id,
        payment_reference=(
            generate_unique_payment_reference(db)
        ),
        transaction_type="refund",
        payment_method="wallet",
        amount=refund_amount,
        status="refunded",
        paid_at=datetime.now(timezone.utc)
    )

    db.add(refund_payment)
    db.flush()

    wallet.balance = balance_after

    wallet_transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=original_payment.user_id,
        reservation_id=original_payment.reservation_id,
        payment_id=refund_payment.id,
        transaction_reference=(
            generate_wallet_transaction_reference(db)
        ),
        transaction_type="refund",
        direction="credit",
        amount=refund_amount,
        balance_before=balance_before,
        balance_after=balance_after,
        description=(
            f"Refund for payment "
            f"{original_payment.payment_reference}."
        )
    )

    db.add(wallet_transaction)

    original_payment.status = "refunded"

    db.commit()

    db.refresh(original_payment)
    db.refresh(refund_payment)

    return (
        original_payment,
        refund_payment
    )


def get_admin_payments(
    db: Session
) -> list[dict]:
    from app.models.user import User

    statement = (
        select(
            Payment,
            User.full_name,
            User.email
        )
        .join(
            User,
            User.id == Payment.user_id
        )
        .order_by(
            Payment.created_at.desc()
        )
    )

    rows = db.execute(statement).all()

    results = []

    for payment, full_name, email in rows:
        is_refundable = (
            payment.transaction_type == "parking_charge"
            and payment.payment_method == "wallet"
            and payment.status == "paid"
        )

        results.append(
            {
                "id": payment.id,
                "user_id": payment.user_id,
                "user_name": full_name,
                "user_email": email,
                "reservation_id": payment.reservation_id,
                "parking_session_id": (
                    payment.parking_session_id
                ),
                "related_payment_id": (
                    payment.related_payment_id
                ),
                "payment_reference": (
                    payment.payment_reference
                ),
                "transaction_type": (
                    payment.transaction_type
                ),
                "payment_method": (
                    payment.payment_method
                ),
                "amount": payment.amount,
                "status": payment.status,
                "paid_at": payment.paid_at,
                "created_at": payment.created_at,
                "is_refundable": is_refundable,
            }
        )

    return results
