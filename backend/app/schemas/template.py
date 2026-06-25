from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

TemplateType = Literal["intro", "followup", "informational"]
TemplateTier = Literal["A", "B", "C"]


class TemplateCreate(BaseModel):
    name: str
    template_type: TemplateType
    tier: TemplateTier | None = None
    content: str
    variables: list[str] | None = None
    success_rate: float | None = None
    created_by: UUID | None = None


class TemplateUpdate(BaseModel):
    name: str | None = None
    template_type: TemplateType | None = None
    tier: TemplateTier | None = None
    content: str | None = None
    variables: list[str] | None = None
    success_rate: float | None = None
    created_by: UUID | None = None


class TemplateRead(TemplateCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
