from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ContactSource = Literal["manual", "linkedin", "github", "apollo", "hunter", "arxiv", "other"]
AffinityType = Literal["alumni", "colombian", "latino", "recruiter", "engineer", "none", "unknown"]


class ContactBase(BaseModel):
    company_id: UUID
    full_name: str = Field(min_length=1, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    linkedin_url: str | None = Field(default=None, max_length=2048)
    github_handle: str | None = Field(default=None, max_length=120)
    twitter_handle: str | None = Field(default=None, max_length=120)
    source: ContactSource = "manual"
    affinity_type: AffinityType = "unknown"
    affinity_score: int | None = Field(default=None, ge=0, le=100)
    role_relevance: int | None = Field(default=None, ge=0, le=100)
    total_score: int | None = Field(default=None, ge=0, le=100)
    metadata: dict[str, Any] | None = None
    contacted: bool = False
    refreshed_at: datetime | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    company_id: UUID | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    linkedin_url: str | None = Field(default=None, max_length=2048)
    github_handle: str | None = Field(default=None, max_length=120)
    twitter_handle: str | None = Field(default=None, max_length=120)
    source: ContactSource | None = None
    affinity_type: AffinityType | None = None
    affinity_score: int | None = Field(default=None, ge=0, le=100)
    role_relevance: int | None = Field(default=None, ge=0, le=100)
    total_score: int | None = Field(default=None, ge=0, le=100)
    metadata: dict[str, Any] | None = None
    contacted: bool | None = None
    refreshed_at: datetime | None = None


class ContactRead(ContactBase):
    id: UUID
    created_at: datetime
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="contact_metadata")

    model_config = ConfigDict(from_attributes=True)
