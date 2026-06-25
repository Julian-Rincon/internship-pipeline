from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

InternFriendly = Literal["green", "yellow", "red", "unknown"]


class VisaDataCreate(BaseModel):
    company_id: UUID
    country: str
    intern_friendly: InternFriendly = "unknown"
    visa_type: str | None = None
    sponsor_verified: bool = False
    evidence_url: str | None = None
    notes: str | None = None
    last_verified: date | None = None


class VisaDataUpdate(BaseModel):
    company_id: UUID | None = None
    country: str | None = None
    intern_friendly: InternFriendly | None = None
    visa_type: str | None = None
    sponsor_verified: bool | None = None
    evidence_url: str | None = None
    notes: str | None = None
    last_verified: date | None = None


class VisaDataRead(VisaDataCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
