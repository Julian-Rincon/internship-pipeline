"""add company ownership fields

Revision ID: 0006_add_company_ownership
Revises: 0005_create_discovery
Create Date: 2026-05-10 16:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_add_company_ownership"
down_revision: str | None = "0005_create_discovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("owner_user_id", sa.Uuid(), nullable=True))
    op.add_column(
        "companies",
        sa.Column("ownership_status", sa.Text(), server_default="unclaimed", nullable=False),
    )
    op.add_column("companies", sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("companies", sa.Column("ownership_notes", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_companies_owner_user_id_users",
        "companies",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_companies_ownership_status",
        "companies",
        "ownership_status IN ('unclaimed', 'claimed', 'paused', 'done')",
    )
    op.create_index("idx_companies_owner_user_id", "companies", ["owner_user_id"])
    op.create_index("idx_companies_ownership_status", "companies", ["ownership_status"])


def downgrade() -> None:
    op.drop_index("idx_companies_ownership_status", table_name="companies")
    op.drop_index("idx_companies_owner_user_id", table_name="companies")
    op.drop_constraint("ck_companies_ownership_status", "companies", type_="check")
    op.drop_constraint("fk_companies_owner_user_id_users", "companies", type_="foreignkey")
    op.drop_column("companies", "ownership_notes")
    op.drop_column("companies", "claimed_at")
    op.drop_column("companies", "ownership_status")
    op.drop_column("companies", "owner_user_id")
