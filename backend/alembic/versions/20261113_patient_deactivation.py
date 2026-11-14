"""Add patient deactivation state.

Revision ID: 20261113_patient_deactivation
Revises: 20260829_chart_confidence
Create Date: 2026-11-13
"""

import sqlalchemy as sa

from alembic import op

revision = "20261113_patient_deactivation"
down_revision = "9c4d2a7f61e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "patient",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("patient", "is_active")
