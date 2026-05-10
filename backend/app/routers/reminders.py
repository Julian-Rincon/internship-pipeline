from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.reminder import ReminderRead
from app.services.reminders import compute_reminders

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("", response_model=list[ReminderRead])
async def list_reminders(
    days_ahead: int = Query(default=7, ge=0, le=365),
    include_resolved: bool = False,
    user_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[ReminderRead]:
    return await compute_reminders(
        db,
        days_ahead=days_ahead,
        include_resolved=include_resolved,
        user_id=user_id,
    )
