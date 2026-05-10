"""create companies table

Revision ID: 0001_create_companies
Revises:
Create Date: 2026-05-09 22:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_companies"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("tier", sa.String(length=1), nullable=True),
        sa.Column("country", sa.Text(), nullable=True),
        sa.Column("region", sa.Text(), nullable=True),
        sa.Column("careers_url", sa.Text(), nullable=True),
        sa.Column("ats_type", sa.Text(), nullable=True),
        sa.Column("visa_friendly_intern", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("tier IS NULL OR tier IN ('A', 'B', 'C')", name="ck_companies_tier"),
        sa.CheckConstraint(
            "visa_friendly_intern IS NULL OR visa_friendly_intern IN ('green', 'yellow', 'red', 'unknown')",
            name="ck_companies_visa_friendly_intern",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'paused', 'rejected', 'won')",
            name="ck_companies_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain", name="uq_companies_domain"),
    )
    op.create_index("idx_companies_tier", "companies", ["tier"])


def downgrade() -> None:
    op.drop_index("idx_companies_tier", table_name="companies")
    op.drop_table("companies")

