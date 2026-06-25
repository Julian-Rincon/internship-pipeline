from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

OutreachChannel = Literal["email", "linkedin", "twitter", "other"]
OutreachStatus = Literal["draft", "sent", "bounced", "replied"]
ReplySentiment = Literal["positive", "neutral", "negative"]


class OutreachLogCreate(BaseModel):
    contact_id: UUID | None = None
    user_id: UUID | None = None
    company_id: UUID | None = None
    channel: OutreachChannel = "email"
    subject: str | None = None
    body: str
    template_id: UUID | None = None
    status: OutreachStatus = "draft"
    sent_at: datetime | None = None
    replied_at: datetime | None = None
    reply_sentiment: ReplySentiment | None = None


class OutreachLogUpdate(BaseModel):
    contact_id: UUID | None = None
    user_id: UUID | None = None
    company_id: UUID | None = None
    channel: OutreachChannel | None = None
    subject: str | None = None
    body: str | None = None
    template_id: UUID | None = None
    status: OutreachStatus | None = None
    sent_at: datetime | None = None
    replied_at: datetime | None = None
    reply_sentiment: ReplySentiment | None = None


class OutreachLogRead(OutreachLogCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
