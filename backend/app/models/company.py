from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        CheckConstraint("tier IS NULL OR tier IN ('A', 'B', 'C')", name="ck_companies_tier"),
        CheckConstraint(
            "visa_friendly_intern IS NULL OR visa_friendly_intern IN ('green', 'yellow', 'red', 'unknown')",
            name="ck_companies_visa_friendly_intern",
        ),
        CheckConstraint(
            "status IN ('active', 'paused', 'rejected', 'won')",
            name="ck_companies_status",
        ),
        CheckConstraint(
            "ownership_status IN ('unclaimed', 'claimed', 'paused', 'done')",
            name="ck_companies_ownership_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(Text, unique=True)
    tier: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)
    careers_url: Mapped[str | None] = mapped_column(Text)
    ats_type: Mapped[str | None] = mapped_column(Text)
    visa_friendly_intern: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active", server_default="active")
    owner_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    ownership_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="unclaimed",
        server_default="unclaimed",
    )
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ownership_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
