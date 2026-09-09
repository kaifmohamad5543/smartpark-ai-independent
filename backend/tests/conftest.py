import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db

# Explicitly import every SQLAlchemy model so that all tables are
# registered in Base.metadata before create_all() is executed.
from app.models.notification import Notification
from app.models.parking_location import ParkingLocation
from app.models.parking_session import ParkingSession
from app.models.parking_space import ParkingSpace
from app.models.payment import Payment
from app.models.prediction import Prediction
from app.models.reservation import Reservation
from app.models.review import Review
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

from app.main import app


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    (
        "postgresql://smartpark_user:smartpark_password"
        "@localhost:5432/smartpark_test_db"
    ),
)

test_database_name = make_url(
    TEST_DATABASE_URL
).database

if not test_database_name or "test" not in test_database_name.lower():
    raise RuntimeError(
        "Refusing to run tests against a non-test database."
    )


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def clear_test_data():
    table_names = ", ".join(
        f'"{table_name}"'
        for table_name in Base.metadata.tables
    )

    with test_engine.begin() as connection:
        connection.execute(
            text(
                f"TRUNCATE TABLE {table_names} "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture(autouse=True)
def reset_test_database():
    # Preserve the Alembic-managed database schema.
    # Only application data is removed between tests.
    clear_test_data()

    yield

    clear_test_data()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
