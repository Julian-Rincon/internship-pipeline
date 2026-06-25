from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class VisaData(Base):
    __tablename__ = "visa_data"
    __table_args__ = (
        CheckConstraint(
            "intern_friendly IN ('green', 'yellow', 'red', 'unknown')",
            name="ck_visa_data_intern_friendly",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    country: Mapped[str] = mapped_column(Text, nullable=False)
    intern_friendly: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    visa_type: Mapped[str | None] = mapped_column(Text)
    sponsor_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    evidence_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    last_verified: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
