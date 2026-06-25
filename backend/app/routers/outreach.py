from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.outreach_log import OutreachLog
from app.schemas.outreach_log import OutreachLogCreate, OutreachLogRead, OutreachLogUpdate
from app.services.outreach_generator import generate_draft, check_daily_limit

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("", response_model=list[OutreachLogRead])
async def list_outreach(
    user_id: UUID | None = None,
    company_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> list[OutreachLog]:
    q = select(OutreachLog).order_by(OutreachLog.created_at.desc())
    if user_id:
        q = q.where(OutreachLog.user_id == user_id)
    if company_id:
        q = q.where(OutreachLog.company_id == company_id)
    if status_filter:
        q = q.where(OutreachLog.status == status_filter)
    result = await db.scalars(q)
    return list(result)


@router.post("", response_model=OutreachLogRead, status_code=status.HTTP_201_CREATED)
async def create_outreach(
    payload: OutreachLogCreate,
    db: AsyncSession = Depends(get_db),
) -> OutreachLog:
    log = OutreachLog(**payload.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.post("/draft", response_model=OutreachLogRead, status_code=status.HTTP_201_CREATED)
async def create_draft(
    contact_id: UUID,
    user_id: UUID,
    template_id: UUID,
    company_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> OutreachLog:
    body = await generate_draft(
        contact_id=contact_id,
        user_id=user_id,
        template_id=template_id,
        db=db,
    )
    log = OutreachLog(
        contact_id=contact_id,
        user_id=user_id,
        company_id=company_id,
        template_id=template_id,
        body=body,
        status="draft",
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.post("/{log_id}/send", response_model=OutreachLogRead)
async def send_outreach(log_id: UUID, db: AsyncSession = Depends(get_db)) -> OutreachLog:
    log = await db.get(OutreachLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Outreach log not found.")
    if log.status != "draft":
        raise HTTPException(status_code=422, detail="Only draft outreach can be sent.")
    if log.user_id and not await check_daily_limit(log.user_id, db):
        raise HTTPException(status_code=429, detail="Daily outreach limit reached (20/day).")
    log.status = "sent"
    log.sent_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(log)
    return log


@router.patch("/{log_id}", response_model=OutreachLogRead)
async def update_outreach(
    log_id: UUID, payload: OutreachLogUpdate, db: AsyncSession = Depends(get_db)
) -> OutreachLog:
    log = await db.get(OutreachLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Outreach log not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    await db.commit()
    await db.refresh(log)
    return log


@router.post("/{log_id}/mark-replied", response_model=OutreachLogRead)
async def mark_replied(
    log_id: UUID,
    reply_sentiment: Literal["positive", "neutral", "negative"] | None = None,
    db: AsyncSession = Depends(get_db),
) -> OutreachLog:
    log = await db.get(OutreachLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Outreach log not found.")
    log.replied_at = datetime.now(UTC)
    log.reply_sentiment = reply_sentiment
    log.status = "replied"
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/{log_id}", response_model=OutreachLogRead)
async def get_outreach(log_id: UUID, db: AsyncSession = Depends(get_db)) -> OutreachLog:
    log = await db.get(OutreachLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Outreach log not found.")
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outreach(log_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    log = await db.get(OutreachLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Outreach log not found.")
    if log.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft outreach can be deleted.")
    await db.delete(log)
    await db.commit()
    return Response(status_code=204)
