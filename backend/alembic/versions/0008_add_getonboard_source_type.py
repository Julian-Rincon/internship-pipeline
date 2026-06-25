"""add getonboard to discovery source type constraint

Revision ID: 0008_add_getonboard_source_type
Revises: 0007_create_discovery_sources
Create Date: 2026-06-24 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0008_add_getonboard_source_type"
down_revision: str | None = "0007_create_discovery_sources"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_discovery_sources_source_type", "discovery_sources", type_="check")
    op.create_check_constraint(
        "ck_discovery_sources_source_type",
        "discovery_sources",
        "source_type IN ('greenhouse', 'lever', 'ashby', 'getonboard')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_discovery_sources_source_type", "discovery_sources", type_="check")
    op.create_check_constraint(
        "ck_discovery_sources_source_type",
        "discovery_sources",
        "source_type IN ('greenhouse', 'lever', 'ashby')",
    )
