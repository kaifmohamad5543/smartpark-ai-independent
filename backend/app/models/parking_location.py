import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Time,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParkingLocation(Base):
    __tablename__ = "parking_locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    postcode: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    total_spaces: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    hourly_rate: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False
    )

    opening_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    closing_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    is_24_hours: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    dynamic_pricing_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
