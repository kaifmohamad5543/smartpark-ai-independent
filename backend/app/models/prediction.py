import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    parking_location_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "parking_locations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    previous_occupancy: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    # Persisted for prediction reproducibility.
    # Nullable so historical prediction rows remain valid.
    current_occupancy: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    traffic_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    weather: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    event_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    parking_price: Mapped[
        Decimal
    ] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    available_spaces: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
    )

    # Capacity actually supplied to the ML model.
    total_spaces: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    # Exact trained model bundle version.
    model_version: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True,
    )

    predicted_occupancy: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    predicted_availability: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
