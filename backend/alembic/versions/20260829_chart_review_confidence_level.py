"""Store chart-review confidence as an explicit level.

Revision ID: 20260829_chart_confidence
Revises:
Create Date: 2026-08-29
"""

import sqlalchemy as sa

from alembic import op

revision = "20260829_chart_confidence"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE chart_review SET confidence = NULL WHERE confidence IS NOT NULL")
    op.alter_column(
        "chart_review",
        "confidence",
        existing_type=sa.Float(),
        type_=sa.String(length=10),
        postgresql_using="confidence::varchar",
        existing_nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE chart_review SET confidence = NULL WHERE confidence IS NOT NULL")
    op.alter_column(
        "chart_review",
        "confidence",
        existing_type=sa.String(length=10),
        type_=sa.Float(),
        postgresql_using="confidence::double precision",
        existing_nullable=True,
    )
