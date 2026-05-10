"""create contacts table

Revision ID: 0003_create_contacts
Revises: 0002_create_users
Create Date: 2026-05-10 00:15:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_create_contacts"
down_revision: str | None = "0002_create_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("github_handle", sa.Text(), nullable=True),
        sa.Column("twitter_handle", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), server_default="manual", nullable=False),
        sa.Column("affinity_type", sa.Text(), server_default="unknown", nullable=False),
        sa.Column("affinity_score", sa.Integer(), nullable=True),
        sa.Column("role_relevance", sa.Integer(), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("contacted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "source IN ('manual', 'linkedin', 'github', 'apollo', 'hunter', 'arxiv', 'other')",
            name="ck_contacts_source",
        ),
        sa.CheckConstraint(
            "affinity_type IN ('alumni', 'colombian', 'latino', 'recruiter', 'engineer', 'none', 'unknown')",
            name="ck_contacts_affinity_type",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_contacts_company_id", "contacts", ["company_id"])
    op.create_index("idx_contacts_total_score", "contacts", ["total_score"])


def downgrade() -> None:
    op.drop_index("idx_contacts_total_score", table_name="contacts")
    op.drop_index("idx_contacts_company_id", table_name="contacts")
    op.drop_table("contacts")

