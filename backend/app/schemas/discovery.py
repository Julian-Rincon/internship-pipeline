from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.application import ApplicationStatus, ApplicationType

DiscoveryCandidateStatus = Literal["pending_review", "approved", "rejected", "ignored"]
JobPostingStatus = Literal["open", "closed", "archived"]
DiscoverySourceType = Literal["greenhouse", "lever", "ashby", "getonboard"]


class JobPostingRead(BaseModel):
    id: UUID
    company_id: UUID | None
    title: str
    url: str
    location: str | None
    remote: bool | None
    description: str | None
    source: str
    detected_at: datetime
    closed_at: datetime | None
    status: JobPostingStatus

    model_config = ConfigDict(from_attributes=True)


class JobPostingCompanyLink(BaseModel):
    company_id: UUID


class JobPostingApplicationCreate(BaseModel):
    user_id: UUID
    contact_id: UUID | None = None
    type: ApplicationType = "formal"
    status: ApplicationStatus = "researching"
    next_action: str | None = Field(default=None, max_length=2048)
    next_action_due: date | None = None
    notes: str | None = None


class DiscoveryCandidateBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    careers_url: str | None = Field(default=None, max_length=2048)
    source: str = Field(min_length=1, max_length=120)
    source_url: str | None = Field(default=None, max_length=2048)
    detected_job_title: str | None = Field(default=None, max_length=255)
    detected_job_url: str | None = Field(default=None, max_length=2048)
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    ats_type: str | None = Field(default=None, max_length=120)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    status: DiscoveryCandidateStatus = "pending_review"
    notes: str | None = None


class DiscoveryCandidateUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    careers_url: str | None = Field(default=None, max_length=2048)
    source: str | None = Field(default=None, min_length=1, max_length=120)
    source_url: str | None = Field(default=None, max_length=2048)
    detected_job_title: str | None = Field(default=None, max_length=255)
    detected_job_url: str | None = Field(default=None, max_length=2048)
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    ats_type: str | None = Field(default=None, max_length=120)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    status: DiscoveryCandidateStatus | None = None
    notes: str | None = None


class DiscoveryCandidateRead(DiscoveryCandidateBase):
    id: UUID
    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class DemoDiscoveryResult(BaseModel):
    candidates_created: int
    job_postings_created: int
    candidates: list[DiscoveryCandidateRead]


class DiscoverySourceBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: DiscoverySourceType
    source_key: str = Field(min_length=1, max_length=255)
    base_url: str | None = Field(default=None, max_length=2048)
    company_hint: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    enabled: bool = True


class DiscoverySourceCreate(DiscoverySourceBase):
    pass


class DiscoverySourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: DiscoverySourceType | None = None
    source_key: str | None = Field(default=None, min_length=1, max_length=255)
    base_url: str | None = Field(default=None, max_length=2048)
    company_hint: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    enabled: bool | None = None


class DiscoverySourceRead(DiscoverySourceBase):
    id: UUID
    last_run_at: datetime | None
    last_status: str | None
    last_error: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscoverySourceRunResult(BaseModel):
    source_id: UUID
    source_name: str
    fetched_count: int
    internship_like_count: int
    candidates_created: int
    candidates_skipped: int
    job_postings_created: int
    errors: list[str]
