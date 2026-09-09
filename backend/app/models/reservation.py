import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    __table_args__ = (
        CheckConstraint(
            "reserved_until > reserved_from",
            name="ck_reservation_valid_time_range"
        ),
        CheckConstraint(
            "pricing_multiplier IS NULL "
            "OR pricing_multiplier > 0",
            name=(
                "ck_reservation_"
                "pricing_multiplier_positive"
            )
        ),
        CheckConstraint(
            "current_occupancy_at_booking IS NULL "
            "OR (current_occupancy_at_booking >= 0 "
            "AND current_occupancy_at_booking <= 100)",
            name=(
                "ck_reservation_"
                "current_occupancy_range"
            )
        ),
        CheckConstraint(
            "predicted_occupancy_at_booking IS NULL "
            "OR (predicted_occupancy_at_booking >= 0 "
            "AND predicted_occupancy_at_booking <= 100)",
            name=(
                "ck_reservation_"
                "predicted_occupancy_range"
            )
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "vehicles.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    parking_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "parking_locations.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    parking_space_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "parking_spaces.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    booking_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False
    )

    reserved_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    reserved_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="confirmed",
        nullable=False,
        index=True
    )

    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    base_hourly_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    applied_hourly_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    pricing_multiplier: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(6, 4),
        nullable=True
    )

    current_occupancy_at_booking: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )

    predicted_occupancy_at_booking: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )

    pricing_model_version: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True
    )

    final_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    checked_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
