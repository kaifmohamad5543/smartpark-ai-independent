import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    __table_args__ = (
        UniqueConstraint(
            "parking_location_id",
            "space_number",
            name="uq_parking_location_space_number"
        ),
        CheckConstraint(
            (
                "ev_charger_status IS NULL OR "
                "ev_charger_status IN "
                "('available', 'occupied', 'offline', 'maintenance')"
            ),
            name="ck_parking_space_ev_charger_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    parking_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "parking_locations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    space_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    space_type: Mapped[str] = mapped_column(
        String(30),
        default="standard",
        nullable=False
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    has_ev_charging: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    ev_charger_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    ev_charger_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_accessible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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
