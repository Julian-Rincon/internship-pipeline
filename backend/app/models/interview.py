from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint(
            "interview_type IN ('phone', 'technical', 'system_design', 'behavioral', 'onsite', 'hr')",
            name="ck_interviews_interview_type",
        ),
        CheckConstraint(
            "outcome IN ('passed', 'failed', 'pending')",
            name="ck_interviews_outcome",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    interview_type: Mapped[str] = mapped_column(Text, nullable=False)
    interviewer_role: Mapped[str | None] = mapped_column(Text)
    questions: Mapped[list[Any] | None] = mapped_column(JSONB)
    outcome: Mapped[str] = mapped_column(Text, nullable=False, default="pending", server_default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
