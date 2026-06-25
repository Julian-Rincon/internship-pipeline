from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class OutreachLog(Base):
    __tablename__ = "outreach_log"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('email', 'linkedin', 'twitter', 'other')",
            name="ck_outreach_log_channel",
        ),
        CheckConstraint(
            "status IN ('draft', 'sent', 'bounced', 'replied')",
            name="ck_outreach_log_status",
        ),
        CheckConstraint(
            "reply_sentiment IS NULL OR reply_sentiment IN ('positive', 'neutral', 'negative')",
            name="ck_outreach_log_reply_sentiment",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    contact_id: Mapped[UUID | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    company_id: Mapped[UUID | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    channel: Mapped[str] = mapped_column(Text, nullable=False, default="email", server_default="email")
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    template_id: Mapped[UUID | None] = mapped_column(ForeignKey("templates.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft", server_default="draft")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reply_sentiment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
