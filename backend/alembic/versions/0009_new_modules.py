"""add interviews, visa_data, templates, outreach_log

Revision ID: 0009_new_modules
Revises: 0008_add_getonboard_source_type
Create Date: 2026-06-25 00:00:00.000000
"""

from collections.abc import Sequence
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op

revision: str = "0009_new_modules"
down_revision: str | None = "0008_add_getonboard_source_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interview_type", sa.Text(), nullable=False),
        sa.Column("interviewer_role", sa.Text(), nullable=True),
        sa.Column("questions", JSONB(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "interview_type IN ('phone','technical','system_design','behavioral','onsite','hr')",
            name="ck_interviews_type",
        ),
        sa.CheckConstraint(
            "outcome IN ('passed','failed','pending')",
            name="ck_interviews_outcome",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "visa_data",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("country", sa.Text(), nullable=False),
        sa.Column("intern_friendly", sa.Text(), nullable=False, server_default="unknown"),
        sa.Column("visa_type", sa.Text(), nullable=True),
        sa.Column("sponsor_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("evidence_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("last_verified", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "intern_friendly IN ('green','yellow','red','unknown')",
            name="ck_visa_intern_friendly",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("template_type", sa.Text(), nullable=False),
        sa.Column("tier", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("variables", JSONB(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "template_type IN ('intro','followup','informational')",
            name="ck_templates_type",
        ),
        sa.CheckConstraint(
            "tier IS NULL OR tier IN ('A','B','C')",
            name="ck_templates_tier",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "outreach_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contact_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("company_id", sa.UUID(), nullable=True),
        sa.Column("channel", sa.Text(), nullable=False, server_default="email"),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reply_sentiment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "channel IN ('email','linkedin','twitter','other')",
            name="ck_outreach_log_channel",
        ),
        sa.CheckConstraint(
            "status IN ('draft','sent','bounced','replied')",
            name="ck_outreach_log_status",
        ),
        sa.CheckConstraint(
            "reply_sentiment IS NULL OR reply_sentiment IN ('positive','neutral','negative')",
            name="ck_outreach_log_sentiment",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("outreach_log")
    op.drop_table("templates")
    op.drop_table("visa_data")
    op.drop_table("interviews")
