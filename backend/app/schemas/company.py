from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CompanyTier = Literal["A", "B", "C"]
VisaFriendly = Literal["green", "yellow", "red", "unknown"]
CompanyStatus = Literal["active", "paused", "rejected", "won"]
OwnershipStatus = Literal["unclaimed", "claimed", "paused", "done"]
OwnedCompanyStatus = Literal["claimed", "paused", "done"]


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


class CompanyClaim(BaseModel):
    user_id: UUID
    ownership_notes: str | None = None


class CompanyOwnershipUpdate(BaseModel):
    ownership_status: OwnedCompanyStatus | None = None
    ownership_notes: str | None = None


class CompanyRead(CompanyBase):
    id: UUID
    owner_user_id: UUID | None
    ownership_status: OwnershipStatus
    claimed_at: datetime | None
    ownership_notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
