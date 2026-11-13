"""Add persistent X-ray review jobs.

Revision ID: 9c4d2a7f61e3
Revises: 48b3bb684508
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9c4d2a7f61e3"
down_revision: str | Sequence[str] | None = "48b3bb684508"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "xray_scan",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("clinical_document_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["clinical_document_id"], ["clinical_document.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_xray_scan_patient_id", "xray_scan", ["patient_id"])
    op.create_index("ix_xray_scan_clinical_document_id", "xray_scan", ["clinical_document_id"])
    op.create_index("ix_xray_scan_status", "xray_scan", ["status"])


def downgrade() -> None:
    op.drop_index("ix_xray_scan_status", table_name="xray_scan")
    op.drop_index("ix_xray_scan_clinical_document_id", table_name="xray_scan")
    op.drop_index("ix_xray_scan_patient_id", table_name="xray_scan")
    op.drop_table("xray_scan")
