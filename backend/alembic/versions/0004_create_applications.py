"""create applications table

Revision ID: 0004_create_applications
Revises: 0003_create_contacts
Create Date: 2026-05-10 01:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_create_applications"
down_revision: str | None = "0003_create_contacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("contact_id", sa.Uuid(), nullable=True),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("next_action_due", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "type IN ('formal', 'speculative', 'referral', 'networking', 'other')",
            name="ck_applications_type",
        ),
        sa.CheckConstraint(
            "status IN ('researching', 'contacted', 'responded', 'interviewing', 'offer', 'rejected', 'paused')",
            name="ck_applications_status",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_applications_company_id", "applications", ["company_id"])
    op.create_index("idx_applications_user_id", "applications", ["user_id"])
    op.create_index("idx_applications_status", "applications", ["status"])


def downgrade() -> None:
    op.drop_index("idx_applications_status", table_name="applications")
    op.drop_index("idx_applications_user_id", table_name="applications")
    op.drop_index("idx_applications_company_id", table_name="applications")
    op.drop_table("applications")

