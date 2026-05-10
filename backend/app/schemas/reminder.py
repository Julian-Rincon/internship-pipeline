from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

ReminderType = Literal[
    "application_overdue",
    "application_due_today",
    "application_due_soon",
    "discovery_pending_review",
    "claimed_company_stale",
]
ReminderSeverity = Literal["low", "medium", "high"]
RelatedEntityType = Literal["application", "discovery_candidate", "company"]


class ReminderRead(BaseModel):
    id: str
    type: ReminderType
    severity: ReminderSeverity
    title: str
    description: str
    related_entity_type: RelatedEntityType
    related_entity_id: str
    due_date: date | None
    created_reference_date: date
    metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ReminderSummaryRead(BaseModel):
    total_reminders: int
    high_count: int
    medium_count: int
    low_count: int
    overdue_count: int
    due_today_count: int
    due_soon_count: int
    pending_review_count: int
    top_items: list[ReminderRead]
