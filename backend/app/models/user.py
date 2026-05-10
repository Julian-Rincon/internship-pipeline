from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('member', 'admin')", name="ck_users_role"),
        CheckConstraint(
            "profile_status IN ('incomplete', 'in_progress', 'ready')",
            name="ck_users_profile_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="member", server_default="member")
    profile_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="incomplete",
        server_default="incomplete",
    )
    github_handle: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    portfolio_url: Mapped[str | None] = mapped_column(Text)
    cv_url: Mapped[str | None] = mapped_column(Text)
    target_roles: Mapped[list[str] | None] = mapped_column(JSONB)
    target_regions: Mapped[list[str] | None] = mapped_column(JSONB)
    target_countries: Mapped[list[str] | None] = mapped_column(JSONB)
    target_company_types: Mapped[list[str] | None] = mapped_column(JSONB)
    preferred_industries: Mapped[list[str] | None] = mapped_column(JSONB)
    technical_interests: Mapped[list[str] | None] = mapped_column(JSONB)
    strong_skills: Mapped[list[str] | None] = mapped_column(JSONB)
    learning_goals: Mapped[list[str] | None] = mapped_column(JSONB)
    internship_goals: Mapped[str | None] = mapped_column(Text)
    profile_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

