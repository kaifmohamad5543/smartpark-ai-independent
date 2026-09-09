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


def create_user(db_session):
    user = User(
        full_name="Wallet Test User",
        email="wallet.test@smartpark.com",
        hashed_password=hash_password(
            "SmartParkTest123!"
        ),
        role="user",
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
        registration_number="WLT123",
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
        name="Wallet Test Parking",
        address="20 Wallet Road",
        city="London",
        postcode="E1 3AB",
        latitude=51.516,
        longitude=-0.071,
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

    return location, space


def create_checked_in_reservation(
    client,
    db_session,
    user,
    vehicle,
    location,
):
    start = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    response = client.post(
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

    assert response.status_code == 201

    created = response.json()

    check_in = client.post(
        "/api/reservations/check-in",
        json={
            "booking_code": created[
                "booking_code"
            ]
        },
        headers=auth_headers(user),
    )

    assert check_in.status_code == 200

    reservation = db_session.get(
        Reservation,
        created["id"],
    )

    db_session.refresh(reservation)

    session = db_session.scalar(
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
    session.started_at = two_hours_ago

    db_session.commit()

    return reservation


def test_wallet_is_created_with_zero_balance(
    client,
    db_session,
):
    user = create_user(db_session)

    response = client.get(
        "/api/wallet",
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == str(user.id)
    assert Decimal(
        str(data["balance"])
    ) == Decimal("0.00")

    wallet = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    assert wallet is not None
    assert wallet.balance == Decimal("0.00")


def test_wallet_top_up_creates_credit_transaction(
    client,
    db_session,
):
    user = create_user(db_session)

    response = client.post(
        "/api/wallet/top-up",
        json={
            "amount": "50.00"
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(
        str(data["wallet"]["balance"])
    ) == Decimal("50.00")

    transaction = data["transaction"]

    assert transaction[
        "transaction_type"
    ] == "top_up"

    assert transaction["direction"] == "credit"

    assert Decimal(
        str(transaction["amount"])
    ) == Decimal("50.00")

    assert Decimal(
        str(transaction["balance_before"])
    ) == Decimal("0.00")

    assert Decimal(
        str(transaction["balance_after"])
    ) == Decimal("50.00")

    assert transaction[
        "transaction_reference"
    ].startswith("WLT-")


def test_wallet_transaction_history_is_user_specific(
    client,
    db_session,
):
    user = create_user(db_session)

    client.post(
        "/api/wallet/top-up",
        json={
            "amount": "20.00"
        },
        headers=auth_headers(user),
    )

    client.post(
        "/api/wallet/top-up",
        json={
            "amount": "10.00"
        },
        headers=auth_headers(user),
    )

    response = client.get(
        "/api/wallet/transactions",
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert all(
        item["user_id"] == str(user.id)
        for item in data
    )

    assert all(
        item["transaction_type"] == "top_up"
        for item in data
    )

    amounts = {
        Decimal(str(item["amount"]))
        for item in data
    }

    assert amounts == {
        Decimal("20.00"),
        Decimal("10.00"),
    }


def test_insufficient_wallet_checkout_rolls_back_everything(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location, space = create_parking(
        db_session
    )

    top_up = client.post(
        "/api/wallet/top-up",
        json={
            "amount": "1.00"
        },
        headers=auth_headers(user),
    )

    assert top_up.status_code == 200

    reservation = create_checked_in_reservation(
        client,
        db_session,
        user,
        vehicle,
        location,
    )

    response = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": "wallet"
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 400

    assert (
        "Insufficient wallet balance"
        in response.json()["detail"]
    )

    db_session.expire_all()

    reservation = db_session.get(
        Reservation,
        reservation.id,
    )

    space = db_session.get(
        ParkingSpace,
        space.id,
    )

    session = db_session.scalar(
        select(ParkingSession).where(
            ParkingSession.reservation_id
            == reservation.id
        )
    )

    wallet = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    payment_count = db_session.scalar(
        select(func.count(Payment.id)).where(
            Payment.reservation_id
            == reservation.id
        )
    )

    debit_count = db_session.scalar(
        select(
            func.count(
                WalletTransaction.id
            )
        ).where(
            WalletTransaction.reservation_id
            == reservation.id,
            WalletTransaction.direction
            == "debit",
        )
    )

    assert reservation.status == "checked_in"
    assert reservation.checked_out_at is None
    assert reservation.final_cost is None

    assert space.is_available is False

    assert session.status == "active"
    assert session.ended_at is None
    assert session.final_cost is None

    assert wallet.balance == Decimal("1.00")

    assert payment_count == 0
    assert debit_count == 0


def test_successful_wallet_checkout_updates_ledger_and_balance(
    client,
    db_session,
):
    user = create_user(db_session)
    vehicle = create_vehicle(
        db_session,
        user,
    )
    location, space = create_parking(
        db_session
    )

    top_up = client.post(
        "/api/wallet/top-up",
        json={
            "amount": "20.00"
        },
        headers=auth_headers(user),
    )

    assert top_up.status_code == 200

    reservation = create_checked_in_reservation(
        client,
        db_session,
        user,
        vehicle,
        location,
    )

    response = client.post(
        (
            f"/api/reservations/"
            f"{reservation.id}/check-out"
        ),
        json={
            "payment_method": "wallet"
        },
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["payment_method"] == "wallet"

    final_cost = Decimal(
        str(data["final_cost"])
    )

    assert final_cost == Decimal("9.00")

    db_session.expire_all()

    wallet = db_session.scalar(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )

    payment = db_session.scalar(
        select(Payment).where(
            Payment.reservation_id
            == reservation.id,
            Payment.transaction_type
            == "parking_charge",
        )
    )

    debit = db_session.scalar(
        select(WalletTransaction).where(
            WalletTransaction.reservation_id
            == reservation.id,
            WalletTransaction.direction
            == "debit",
        )
    )

    reservation = db_session.get(
        Reservation,
        reservation.id,
    )

    space = db_session.get(
        ParkingSpace,
        space.id,
    )

    assert wallet.balance == Decimal("11.00")

    assert payment is not None
    assert payment.amount == Decimal("9.00")
    assert payment.payment_method == "wallet"
    assert payment.status == "paid"

    assert debit is not None
    assert debit.payment_id == payment.id
    assert debit.transaction_type == (
        "parking_payment"
    )
    assert debit.amount == Decimal("9.00")
    assert debit.balance_before == Decimal(
        "20.00"
    )
    assert debit.balance_after == Decimal(
        "11.00"
    )

    assert reservation.status == "completed"
    assert space.is_available is True
