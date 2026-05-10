"""create discovery sources table

Revision ID: 0007_create_discovery_sources
Revises: 0006_add_company_ownership
Create Date: 2026-05-10 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_create_discovery_sources"
down_revision: str | None = "0006_add_company_ownership"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discovery_sources",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("source_key", sa.Text(), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("company_hint", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), nullable=True),
        sa.Column("region", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.Text(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "source_type IN ('greenhouse', 'lever', 'ashby')",
            name="ck_discovery_sources_source_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_type", "source_key", name="uq_discovery_sources_type_key"),
    )
    op.create_index("idx_discovery_sources_enabled", "discovery_sources", ["enabled"])
    op.create_index("idx_discovery_sources_source_type", "discovery_sources", ["source_type"])


def downgrade() -> None:
    op.drop_index("idx_discovery_sources_source_type", table_name="discovery_sources")
    op.drop_index("idx_discovery_sources_enabled", table_name="discovery_sources")
    op.drop_table("discovery_sources")
