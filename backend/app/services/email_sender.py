import os
from datetime import UTC, datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.outreach_log import OutreachLog


async def mark_as_sent(outreach_log_id: UUID, db: AsyncSession) -> OutreachLog:
    log = await db.get(OutreachLog, outreach_log_id)
    if log is None:
        raise ValueError(f"OutreachLog {outreach_log_id} not found")
    resend_key = os.getenv("RESEND_API_KEY")
    if resend_key:
        print(f"[EmailSender] RESEND_API_KEY found — real sending TODO. Running dry-run for now.")
    log.status = "sent"
    log.sent_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(log)
    return log
