from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["member", "admin"]
ProfileStatus = Literal["incomplete", "in_progress", "ready"]


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    role: UserRole = "member"
    profile_status: ProfileStatus = "incomplete"
    github_handle: str | None = Field(default=None, max_length=120)
    linkedin_url: str | None = Field(default=None, max_length=2048)
    portfolio_url: str | None = Field(default=None, max_length=2048)
    cv_url: str | None = Field(default=None, max_length=2048)
    target_roles: list[str] | None = None
    target_regions: list[str] | None = None
    target_countries: list[str] | None = None
    target_company_types: list[str] | None = None
    preferred_industries: list[str] | None = None
    technical_interests: list[str] | None = None
    strong_skills: list[str] | None = None
    learning_goals: list[str] | None = None
    internship_goals: str | None = None
    profile_completed_at: datetime | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: UserRole | None = None
    profile_status: ProfileStatus | None = None
    github_handle: str | None = Field(default=None, max_length=120)
    linkedin_url: str | None = Field(default=None, max_length=2048)
    portfolio_url: str | None = Field(default=None, max_length=2048)
    cv_url: str | None = Field(default=None, max_length=2048)
    target_roles: list[str] | None = None
    target_regions: list[str] | None = None
    target_countries: list[str] | None = None
    target_company_types: list[str] | None = None
    preferred_industries: list[str] | None = None
    technical_interests: list[str] | None = None
    strong_skills: list[str] | None = None
    learning_goals: list[str] | None = None
    internship_goals: str | None = None
    profile_completed_at: datetime | None = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

