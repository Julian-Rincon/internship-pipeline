from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text, false, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        CheckConstraint(
            "source IN ('manual', 'linkedin', 'github', 'apollo', 'hunter', 'arxiv', 'other')",
            name="ck_contacts_source",
        ),
        CheckConstraint(
            "affinity_type IN ('alumni', 'colombian', 'latino', 'recruiter', 'engineer', 'none', 'unknown')",
            name="ck_contacts_affinity_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    github_handle: Mapped[str | None] = mapped_column(Text)
    twitter_handle: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, nullable=False, default="manual", server_default="manual")
    affinity_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    affinity_score: Mapped[int | None] = mapped_column(Integer)
    role_relevance: Mapped[int | None] = mapped_column(Integer)
    total_score: Mapped[int | None] = mapped_column(Integer)
    contact_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
    contacted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    refreshed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

