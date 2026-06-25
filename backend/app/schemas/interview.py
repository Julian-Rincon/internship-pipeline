from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

InterviewType = Literal["phone", "technical", "system_design", "behavioral", "onsite", "hr"]
InterviewOutcome = Literal["passed", "failed", "pending"]


class InterviewCreate(BaseModel):
    company_id: UUID
    user_id: UUID
    interview_type: InterviewType
    scheduled_at: datetime | None = None
    interviewer_role: str | None = None
    questions: list[str] | None = None
    outcome: InterviewOutcome = "pending"
    notes: str | None = None


class InterviewUpdate(BaseModel):
    company_id: UUID | None = None
    user_id: UUID | None = None
    interview_type: InterviewType | None = None
    scheduled_at: datetime | None = None
    interviewer_role: str | None = None
    questions: list[str] | None = None
    outcome: InterviewOutcome | None = None
    notes: str | None = None


class InterviewRead(InterviewCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
