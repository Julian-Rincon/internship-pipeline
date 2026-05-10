"""create discovery and job posting tables

Revision ID: 0005_create_discovery
Revises: 0004_create_applications
Create Date: 2026-05-10 14:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_create_discovery"
down_revision: str | None = "0004_create_applications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("remote", sa.Boolean(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), server_default="open", nullable=False),
        sa.CheckConstraint("status IN ('open', 'closed', 'archived')", name="ck_job_postings_status"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index("idx_job_postings_company_id", "job_postings", ["company_id"])
    op.create_index("idx_job_postings_status", "job_postings", ["status"])

    op.create_table(
        "discovery_candidates",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("careers_url", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("detected_job_title", sa.Text(), nullable=True),
        sa.Column("detected_job_url", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), nullable=True),
        sa.Column("region", sa.Text(), nullable=True),
        sa.Column("ats_type", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("status", sa.Text(), server_default="pending_review", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected', 'ignored')",
            name="ck_discovery_candidates_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_discovery_candidates_status", "discovery_candidates", ["status"])
    op.create_index("idx_discovery_candidates_detected_job_url", "discovery_candidates", ["detected_job_url"])


def downgrade() -> None:
    op.drop_index("idx_discovery_candidates_detected_job_url", table_name="discovery_candidates")
    op.drop_index("idx_discovery_candidates_status", table_name="discovery_candidates")
    op.drop_table("discovery_candidates")
    op.drop_index("idx_job_postings_status", table_name="job_postings")
    op.drop_index("idx_job_postings_company_id", table_name="job_postings")
    op.drop_table("job_postings")
