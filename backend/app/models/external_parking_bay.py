import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExternalParkingBay(Base):
    """
    Genuine public parking infrastructure data imported
    from the London Borough of Camden Open Data portal.

    This table stores parking infrastructure information.
    It must not be described as real-time occupancy data.
    """

    __tablename__ = "external_parking_bays"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    source_identifier: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    restriction_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    parking_spaces: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    times_of_operation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    maximum_stay: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    tariff: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cashless_identifier: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    road_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    postcode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    controlled_parking_zone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    valid_parking_permits: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parking_bay_length_metres: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    easting: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    northing: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    spatial_accuracy: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_last_uploaded: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    organisation_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_dataset: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="Camden Parking Bays",
    )

    source_organisation: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="London Borough of Camden",
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=(
            "https://opendata.camden.gov.uk/"
            "resource/7hiv-3r9k"
        ),
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
