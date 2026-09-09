from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select

from app.models.parking_location import ParkingLocation
from app.models.parking_session import ParkingSession
from app.models.parking_space import ParkingSpace
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.utils.security import create_access_token, hash_password


def create_user(
    db_session,
    *,
    email,
    role="user",
):
    user = User(
        full_name=(
            "Refund Administrator"
            if role == "admin"
            else "Refund Test User"
        ),
        email=email,
        hashed_password=hash_password(
            "SmartParkTest123!"
        ),
        role=role,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def auth_headers(user):
    token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "role": user.role,
            "email": user.email,
        },
    )

    return {
        "Authorization": f"Bearer {token}"
    }


def create_vehicle(db_session, user):
    vehicle = Vehicle(
        user_id=user.id,
        registration_number="RFD123",
        make="Toyota",
        model="Corolla",
        colour="Black",
        vehicle_type="car",
        is_default=True,
    )

    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)

    return vehicle


def create_parking(db_session):
    location = ParkingLocation(
        name="Refund Test Parking",
        address="30 Refund Road",
        city="London",
        postcode="E1 4AB",
        latitude=51.517,
        longitude=-0.072,
        total_spaces=1,
        hourly_rate=Decimal("4.50"),
        opening_time=None,
        closing_time=None,
        is_24_hours=True,
        is_active=True,
    )

    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)

    space = ParkingSpace(
        parking_location_id=location.id,
        space_number="A1",
        space_type="standard",
        is_available=True,
        has_ev_charging=False,
        is_accessible=False,
        is_active=True,
    )

    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)

    return location


def create_paid_reservation(
    client,
    db_session,
    user,
    *,
    payment_method,
):
    vehicle = create_vehicle(
        db_session,
        user,
    )

    location = create_parking(
        db_session
    )

    if payment_method == "wallet":
        top_up = client.post(
            "/api/wallet/top-up",
            json={
                "amount": "20.00"
            },
            headers=auth_headers(user),
        )

        assert top_up.status_code == 200

    start = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    reservation_response = client.post(
        "/api/reservations",
        json={
            "vehicle_id": str(vehicle.id),
            "parking_location_id": str(
                location.id
            ),
            "reserved_from": start.isoformat(),
            "reserved_until": (
                start + timedelta(hours=2)
            ).isoformat(),
        },
        headers=auth_headers(user),
    )

    assert reservation_response.status_code == 201

    reservation_data = reservation_response.json()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": reservation_data[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert check_in.status_code == 200

    reservation = db_session.get(
        Reservation,
        reservation_data["id"],
    )

    db_session.refresh(reservation)

    parking_session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    two_hours_ago = (
        datetime.now(timezone.utc)
        - timedelta(hours=2)
    )

    reservation.checked_in_at = two_hours_ago
    parking_session.started_at = two_hours_ago

    db_session.commit()

    checkout = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": payment_method
        },
        headers=auth_headers(user),
    )

    assert checkout.status_code == 200

    db_session.expire_all()

    payment = db_session.scalar(
        select(Payment).where(
            Payment.reservation_id
            == reservation.id,
            Payment.transaction_type
            == "parking_charge",
        )
    )

    assert payment is not None

    return payment


def test_standard_user_cannot_refund_payment(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="refund.user@smartpark.com",
    )

    payment = create_paid_reservation(
        client,
        db_session,
        user,
        payment_method="wallet",
    )

    response = client.post(
        (
            "/api/admin/payments/"
            f"{payment.id}/refund"
        ),
        headers=auth_headers(user),
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "Administrator access is required."
    )


def test_admin_wallet_refund_restores_balance_and_creates_ledger(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="refund.customer@smartpark.com",
    )

    admin = create_user(
        db_session,
        email="refund.admin@smartpark.com",
        role="admin",
    )

    payment = create_paid_reservation(
        client,
        db_session,
        user,
        payment_method="wallet",
    )

    original_amount = Decimal(
        str(payment.amount)
    )

    wallet_before_refund = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    balance_before_refund = Decimal(
        str(wallet_before_refund.balance)
    )

    response = client.post(
        (
            "/api/admin/payments/"
            f"{payment.id}/refund"
        ),
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "original_payment"
    ]["status"] == "refunded"

    refund_data = data["refund_payment"]

    assert refund_data[
        "transaction_type"
    ] == "refund"

    assert refund_data[
        "payment_method"
    ] == "wallet"

    assert Decimal(
        str(refund_data["amount"])
    ) == original_amount

    db_session.expire_all()

    original_payment = db_session.get(
        Payment,
        payment.id,
    )

    refund_payment = db_session.scalar(
        select(Payment).where(
            Payment.related_payment_id
            == original_payment.id,
            Payment.transaction_type
            == "refund",
        )
    )

    wallet = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    refund_transaction = db_session.scalar(
        select(WalletTransaction).where(
            WalletTransaction.payment_id
            == refund_payment.id,
            WalletTransaction.transaction_type
            == "refund",
        )
    )

    assert original_payment.status == "refunded"

    assert refund_payment is not None
    assert refund_payment.related_payment_id == (
        original_payment.id
    )
    assert refund_payment.amount == original_amount

    assert wallet.balance == (
        balance_before_refund
        + original_amount
    )

    assert wallet.balance == Decimal("20.00")

    assert refund_transaction is not None
    assert refund_transaction.direction == "credit"
    assert refund_transaction.amount == original_amount

    assert refund_transaction.balance_before == (
        balance_before_refund
    )

    assert refund_transaction.balance_after == (
        Decimal("20.00")
    )


def test_duplicate_refund_is_rejected_without_extra_credit(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="duplicate.customer@smartpark.com",
    )

    admin = create_user(
        db_session,
        email="duplicate.admin@smartpark.com",
        role="admin",
    )

    payment = create_paid_reservation(
        client,
        db_session,
        user,
        payment_method="wallet",
    )

    first = client.post(
        (
            "/api/admin/payments/"
            f"{payment.id}/refund"
        ),
        headers=auth_headers(admin),
    )

    assert first.status_code == 200

    second = client.post(
        (
            "/api/admin/payments/"
            f"{payment.id}/refund"
        ),
        headers=auth_headers(admin),
    )

    assert second.status_code == 400

    assert second.json()["detail"] == (
        "This payment has already been refunded."
    )

    db_session.expire_all()

    wallet = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    refund_count = db_session.scalar(
        select(func.count(Payment.id)).where(
            Payment.related_payment_id
            == payment.id,
            Payment.transaction_type
            == "refund",
        )
    )

    refund_transaction_count = db_session.scalar(
        select(
            func.count(
                WalletTransaction.id
            )
        ).where(
            WalletTransaction.user_id
            == user.id,
            WalletTransaction.transaction_type
            == "refund",
        )
    )

    assert wallet.balance == Decimal("20.00")
    assert refund_count == 1
    assert refund_transaction_count == 1


def test_card_payment_cannot_use_wallet_refund_flow(
    client,
    db_session,
):
    user = create_user(
        db_session,
        email="card.customer@smartpark.com",
    )

    admin = create_user(
        db_session,
        email="card.admin@smartpark.com",
        role="admin",
    )

    payment = create_paid_reservation(
        client,
        db_session,
        user,
        payment_method="card",
    )

    response = client.post(
        (
            "/api/admin/payments/"
            f"{payment.id}/refund"
        ),
        headers=auth_headers(admin),
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only wallet payments are supported "
        "by this refund flow."
    )

    db_session.expire_all()

    original_payment = db_session.get(
        Payment,
        payment.id,
    )

    assert original_payment.status == "paid"

    refund_count = db_session.scalar(
        select(func.count(Payment.id)).where(
            Payment.related_payment_id
            == payment.id,
            Payment.transaction_type
            == "refund",
        )
    )

    assert refund_count == 0
