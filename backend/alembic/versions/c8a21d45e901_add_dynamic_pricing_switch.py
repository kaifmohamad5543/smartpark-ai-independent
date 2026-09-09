"""add dynamic pricing switch

Revision ID: c8a21d45e901
Revises: b7f3d91a4c22
"""

from alembic import op
import sqlalchemy as sa


revision = "c8a21d45e901"
down_revision = "b7f3d91a4c22"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "parking_locations",
        sa.Column(
            "dynamic_pricing_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column(
        "parking_locations",
        "dynamic_pricing_enabled",
    )
