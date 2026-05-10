from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ApplicationType = Literal["formal", "speculative", "referral", "networking", "other"]
ApplicationStatus = Literal[
    "researching",
    "contacted",
    "responded",
    "interviewing",
    "offer",
    "rejected",
    "paused",
]


class ApplicationBase(BaseModel):
    company_id: UUID
    user_id: UUID
    type: ApplicationType
    status: ApplicationStatus
    contact_id: UUID | None = None
    applied_at: datetime | None = None
    next_action: str | None = Field(default=None, max_length=2048)
    next_action_due: date | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_id: UUID | None = None
    user_id: UUID | None = None
    contact_id: UUID | None = None
    type: ApplicationType | None = None
    status: ApplicationStatus | None = None
    applied_at: datetime | None = None
    next_action: str | None = Field(default=None, max_length=2048)
    next_action_due: date | None = None
    notes: str | None = None


class ApplicationRead(ApplicationBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

