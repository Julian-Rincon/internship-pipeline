from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.reminders import compute_reminders

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def count_rows(db: AsyncSession, model: type) -> int:
    return await db.scalar(select(func.count()).select_from(model)) or 0


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)) -> DashboardSummary:
    status_rows = await db.execute(
        select(Application.status, func.count()).group_by(Application.status)
    )
    ownership_rows = await db.execute(
        select(Company.ownership_status, func.count()).group_by(Company.ownership_status)
    )
    ownership_counts = {status: count for status, count in ownership_rows.all()}
    reminders = await compute_reminders(db)
    reminder_type_counts = {}
    for reminder in reminders:
        reminder_type_counts[reminder.type] = reminder_type_counts.get(reminder.type, 0) + 1

    return DashboardSummary(
        total_companies=await count_rows(db, Company),
        total_users=await count_rows(db, User),
        total_contacts=await count_rows(db, Contact),
        total_applications=await count_rows(db, Application),
        unclaimed_companies=ownership_counts.get("unclaimed", 0),
        claimed_companies=ownership_counts.get("claimed", 0),
        paused_companies=ownership_counts.get("paused", 0),
        done_companies=ownership_counts.get("done", 0),
        overdue_reminders=reminder_type_counts.get("application_overdue", 0),
        due_today_reminders=reminder_type_counts.get("application_due_today", 0),
        due_soon_reminders=reminder_type_counts.get("application_due_soon", 0),
        pending_review_reminders=reminder_type_counts.get("discovery_pending_review", 0),
        applications_by_status={status: count for status, count in status_rows.all()},
    )
