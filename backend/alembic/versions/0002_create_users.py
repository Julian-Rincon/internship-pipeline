"""create users table

Revision ID: 0002_create_users
Revises: 0001_create_companies
Create Date: 2026-05-09 23:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_users"
down_revision: str | None = "0001_create_companies"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), server_default="member", nullable=False),
        sa.Column("profile_status", sa.Text(), server_default="incomplete", nullable=False),
        sa.Column("github_handle", sa.Text(), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("portfolio_url", sa.Text(), nullable=True),
        sa.Column("cv_url", sa.Text(), nullable=True),
        sa.Column("target_roles", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("target_regions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("target_countries", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("target_company_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("preferred_industries", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("technical_interests", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("strong_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("learning_goals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("internship_goals", sa.Text(), nullable=True),
        sa.Column("profile_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('member', 'admin')", name="ck_users_role"),
        sa.CheckConstraint(
            "profile_status IN ('incomplete', 'in_progress', 'ready')",
            name="ck_users_profile_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_profile_status", "users", ["profile_status"])


def downgrade() -> None:
    op.drop_index("idx_users_profile_status", table_name="users")
    op.drop_table("users")

