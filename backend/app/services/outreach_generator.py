import logging
import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def generate_draft(
    contact_id: UUID,
    user_id: UUID,
    template_id: UUID,
    db: AsyncSession,
) -> str:
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.template import Template
    from app.models.user import User

    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=422, detail="Contact not found.")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=422, detail="User not found.")

    template = await db.get(Template, template_id)
    if template is None:
        raise HTTPException(status_code=422, detail="Template not found.")

    company = await db.get(Company, contact.company_id)
    if company is None:
        raise HTTPException(status_code=422, detail="Company not found.")

    variables: dict[str, str] = {
        "company_name": company.name,
        "contact_name": contact.full_name,
        "contact_role": contact.role or "team",
        "user_name": user.name,
        "user_skills": ", ".join((user.strong_skills or [])[:5]),
        "company_tier": company.tier or "B",
    }

    try:
        filled = template.content.format_map(variables)
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Template references unknown variable: {exc}",
        ) from exc

    return filled


async def check_daily_limit(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 20,
) -> bool:
    from app.models.outreach_log import OutreachLog

    today_start = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    stmt = select(func.count()).where(
        OutreachLog.user_id == user_id,
        OutreachLog.sent_at >= today_start,
    )
    count = await db.scalar(stmt)
    if (count or 0) >= limit:
        return False
    return True
