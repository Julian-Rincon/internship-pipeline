from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def count_rows(db: AsyncSession, model: type) -> int:
    return await db.scalar(select(func.count()).select_from(model)) or 0


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)) -> DashboardSummary:
    status_rows = await db.execute(
        select(Application.status, func.count()).group_by(Application.status)
    )

    return DashboardSummary(
        total_companies=await count_rows(db, Company),
        total_users=await count_rows(db, User),
        total_contacts=await count_rows(db, Contact),
        total_applications=await count_rows(db, Application),
        applications_by_status={status: count for status, count in status_rows.all()},
    )

