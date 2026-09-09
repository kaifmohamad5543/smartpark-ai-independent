"""add dynamic pricing to reservations

Revision ID: b7f3d91a4c22
Revises: 9c4e1a7b2f10
"""

from alembic import op
import sqlalchemy as sa


revision = "b7f3d91a4c22"
down_revision = "9c4e1a7b2f10"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "reservations",
        sa.Column(
            "base_hourly_rate",
            sa.Numeric(10, 2),
            nullable=True,
        ),
    )

    op.add_column(
        "reservations",
        sa.Column(
            "applied_hourly_rate",
            sa.Numeric(10, 2),
            nullable=True,
        ),
    )

    op.add_column(
        "reservations",
        sa.Column(
            "pricing_multiplier",
            sa.Numeric(6, 4),
            nullable=True,
        ),
    )

    op.add_column(
        "reservations",
        sa.Column(
            "current_occupancy_at_booking",
            sa.Numeric(6, 2),
            nullable=True,
        ),
    )

    op.add_column(
        "reservations",
        sa.Column(
            "predicted_occupancy_at_booking",
            sa.Numeric(6, 2),
            nullable=True,
        ),
    )

    op.add_column(
        "reservations",
        sa.Column(
            "pricing_model_version",
            sa.String(50),
            nullable=True,
        ),
    )

    op.create_check_constraint(
        "ck_reservation_pricing_multiplier_positive",
        "reservations",
        (
            "pricing_multiplier IS NULL "
            "OR pricing_multiplier > 0"
        ),
    )

    op.create_check_constraint(
        "ck_reservation_current_occupancy_range",
        "reservations",
        (
            "current_occupancy_at_booking IS NULL "
            "OR (current_occupancy_at_booking >= 0 "
            "AND current_occupancy_at_booking <= 100)"
        ),
    )

    op.create_check_constraint(
        "ck_reservation_predicted_occupancy_range",
        "reservations",
        (
            "predicted_occupancy_at_booking IS NULL "
            "OR (predicted_occupancy_at_booking >= 0 "
            "AND predicted_occupancy_at_booking <= 100)"
        ),
    )


def downgrade():
    op.drop_constraint(
        "ck_reservation_predicted_occupancy_range",
        "reservations",
        type_="check",
    )

    op.drop_constraint(
        "ck_reservation_current_occupancy_range",
        "reservations",
        type_="check",
    )

    op.drop_constraint(
        "ck_reservation_pricing_multiplier_positive",
        "reservations",
        type_="check",
    )

    op.drop_column(
        "reservations",
        "pricing_model_version",
    )

    op.drop_column(
        "reservations",
        "predicted_occupancy_at_booking",
    )

    op.drop_column(
        "reservations",
        "current_occupancy_at_booking",
    )

    op.drop_column(
        "reservations",
        "pricing_multiplier",
    )

    op.drop_column(
        "reservations",
        "applied_hourly_rate",
    )

    op.drop_column(
        "reservations",
        "base_hourly_rate",
    )
