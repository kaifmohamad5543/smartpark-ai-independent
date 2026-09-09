"""add EV charger live status

Revision ID: 9c4e1a7b2f10
Revises: 7138a812e802
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4e1a7b2f10"
down_revision: Union[str, Sequence[str], None] = (
    "7138a812e802"
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parking_spaces",
        sa.Column(
            "ev_charger_status",
            sa.String(length=30),
            nullable=True,
        ),
    )

    op.add_column(
        "parking_spaces",
        sa.Column(
            "ev_charger_updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_check_constraint(
        "ck_parking_space_ev_charger_status",
        "parking_spaces",
        (
            "ev_charger_status IS NULL OR "
            "ev_charger_status IN "
            "('available', 'occupied', "
            "'offline', 'maintenance')"
        ),
    )

    op.execute(
        """
        UPDATE parking_spaces
        SET
            ev_charger_status = 'available',
            ev_charger_updated_at = CURRENT_TIMESTAMP
        WHERE has_ev_charging = TRUE
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_parking_space_ev_charger_status",
        "parking_spaces",
        type_="check",
    )

    op.drop_column(
        "parking_spaces",
        "ev_charger_updated_at",
    )

    op.drop_column(
        "parking_spaces",
        "ev_charger_status",
    )
