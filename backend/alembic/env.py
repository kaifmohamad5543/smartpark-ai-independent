import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.database import Base

# Import every SQLAlchemy model so all tables are
# registered in Base.metadata for autogeneration.
from app.models.external_parking_bay import ExternalParkingBay
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


config = context.config


if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


database_url = os.getenv(
    "ALEMBIC_DATABASE_URL",
    settings.database_url,
)

# ConfigParser uses % for interpolation, so escape
# any percent characters that may exist in a URL.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
