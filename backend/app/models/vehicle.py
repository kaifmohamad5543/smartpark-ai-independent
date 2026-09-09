import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    registration_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    make: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(60),
        nullable=False
    )

    colour: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(30),
        default="car",
        nullable=False
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
