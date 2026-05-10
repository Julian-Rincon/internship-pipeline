from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CompanyTier = Literal["A", "B", "C"]
VisaFriendly = Literal["green", "yellow", "red", "unknown"]
CompanyStatus = Literal["active", "paused", "rejected", "won"]


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    tier: CompanyTier | None = None
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    careers_url: str | None = Field(default=None, max_length=2048)
    ats_type: str | None = Field(default=None, max_length=120)
    visa_friendly_intern: VisaFriendly | None = "unknown"
    status: CompanyStatus = "active"


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    tier: CompanyTier | None = None
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    careers_url: str | None = Field(default=None, max_length=2048)
    ats_type: str | None = Field(default=None, max_length=120)
    visa_friendly_intern: VisaFriendly | None = None
    status: CompanyStatus | None = None


class CompanyRead(CompanyBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

