"""add hashed_password to users

Revision ID: 0010_add_user_password
Revises: 0009_new_modules
Create Date: 2026-07-06 00:00:00.000000
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "0010_add_user_password"
down_revision: str | None = "0009_new_modules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
