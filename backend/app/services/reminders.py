from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.company import Company
from app.models.discovery_candidate import DiscoveryCandidate
from app.schemas.reminder import ReminderRead, ReminderSummaryRead

IGNORED_APPLICATION_STATUSES = {"offer", "rejected", "paused"}
STALE_CLAIM_DAYS = 14


async def compute_reminders(
    db: AsyncSession,
    *,
    days_ahead: int = 7,
    include_resolved: bool = False,
    user_id: UUID | None = None,
) -> list[ReminderRead]:
    del include_resolved

    today = date.today()
    horizon = today + timedelta(days=max(days_ahead, 0))
    reminders: list[ReminderRead] = []

    reminders.extend(await _application_reminders(db, today=today, horizon=horizon, user_id=user_id))
    reminders.extend(await _discovery_reminders(db, today=today))
    reminders.extend(await _claimed_company_reminders(db, today=today, user_id=user_id))

    severity_rank = {"high": 0, "medium": 1, "low": 2}
    return sorted(
        reminders,
        key=lambda reminder: (
            severity_rank[reminder.severity],
            reminder.due_date or reminder.created_reference_date,
            reminder.title,
        ),
    )


async def compute_n8n_reminder_summary(
    db: AsyncSession,
    *,
    days_ahead: int = 7,
    include_resolved: bool = False,
    user_id: UUID | None = None,
) -> ReminderSummaryRead:
    reminders = await compute_reminders(
        db,
        days_ahead=days_ahead,
        include_resolved=include_resolved,
        user_id=user_id,
    )

    return ReminderSummaryRead(
        total_reminders=len(reminders),
        high_count=sum(1 for reminder in reminders if reminder.severity == "high"),
        medium_count=sum(1 for reminder in reminders if reminder.severity == "medium"),
        low_count=sum(1 for reminder in reminders if reminder.severity == "low"),
        overdue_count=sum(1 for reminder in reminders if reminder.type == "application_overdue"),
        due_today_count=sum(1 for reminder in reminders if reminder.type == "application_due_today"),
        due_soon_count=sum(1 for reminder in reminders if reminder.type == "application_due_soon"),
        pending_review_count=sum(
            1 for reminder in reminders if reminder.type == "discovery_pending_review"
        ),
        top_items=reminders[:10],
    )


async def _application_reminders(
    db: AsyncSession,
    *,
    today: date,
    horizon: date,
    user_id: UUID | None,
) -> list[ReminderRead]:
    statement = select(Application).where(Application.next_action_due.is_not(None))
    if user_id is not None:
        statement = statement.where(Application.user_id == user_id)

    applications = await db.scalars(statement.order_by(Application.next_action_due.asc()))
    reminders: list[ReminderRead] = []

    for application in applications:
        if application.status in IGNORED_APPLICATION_STATUSES:
            continue

        due_date = application.next_action_due
        if due_date is None:
            continue

        if due_date < today:
            reminders.append(_application_reminder(application, "application_overdue", "high", today))
        elif due_date == today:
            reminders.append(_application_reminder(application, "application_due_today", "medium", today))
        elif today < due_date <= horizon:
            reminders.append(_application_reminder(application, "application_due_soon", "low", today))

    return reminders


def _application_reminder(
    application: Application,
    reminder_type: str,
    severity: str,
    today: date,
) -> ReminderRead:
    labels = {
        "application_overdue": "Application action overdue",
        "application_due_today": "Application action due today",
        "application_due_soon": "Application action due soon",
    }
    due_date = application.next_action_due
    return ReminderRead(
        id=f"{reminder_type}:{application.id}",
        type=reminder_type,
        severity=severity,
        title=labels[reminder_type],
        description=application.next_action or "Review the next manual application action.",
        related_entity_type="application",
        related_entity_id=str(application.id),
        due_date=due_date,
        created_reference_date=today,
        metadata={
            "application_status": application.status,
            "company_id": str(application.company_id),
            "user_id": str(application.user_id),
        },
    )


async def _discovery_reminders(db: AsyncSession, *, today: date) -> list[ReminderRead]:
    candidates = await db.scalars(
        select(DiscoveryCandidate)
        .where(DiscoveryCandidate.status == "pending_review")
        .order_by(DiscoveryCandidate.created_at.asc())
    )

    return [
        ReminderRead(
            id=f"discovery_pending_review:{candidate.id}",
            type="discovery_pending_review",
            severity="medium",
            title="Discovery candidate pending review",
            description=f"Review {candidate.company_name} before adding it to the official company list.",
            related_entity_type="discovery_candidate",
            related_entity_id=str(candidate.id),
            due_date=None,
            created_reference_date=_date_from_datetime(candidate.created_at, today),
            metadata={
                "company_name": candidate.company_name,
                "source": candidate.source,
                "detected_job_title": candidate.detected_job_title,
            },
        )
        for candidate in candidates
    ]


async def _claimed_company_reminders(
    db: AsyncSession,
    *,
    today: date,
    user_id: UUID | None,
) -> list[ReminderRead]:
    stale_before = today - timedelta(days=STALE_CLAIM_DAYS)
    statement = select(Company).where(
        Company.ownership_status == "claimed",
        Company.claimed_at.is_not(None),
    )
    if user_id is not None:
        statement = statement.where(Company.owner_user_id == user_id)

    companies = await db.scalars(statement.order_by(Company.claimed_at.asc()))
    reminders: list[ReminderRead] = []

    for company in companies:
        claimed_date = _date_from_datetime(company.claimed_at, today)
        if claimed_date > stale_before:
            continue

        reminders.append(
            ReminderRead(
                id=f"claimed_company_stale:{company.id}",
                type="claimed_company_stale",
                severity="medium",
                title="Claimed company may need an update",
                description=f"{company.name} has been claimed for at least {STALE_CLAIM_DAYS} days.",
                related_entity_type="company",
                related_entity_id=str(company.id),
                due_date=None,
                created_reference_date=claimed_date,
                metadata={
                    "owner_user_id": str(company.owner_user_id) if company.owner_user_id else None,
                    "ownership_status": company.ownership_status,
                    "claimed_at": company.claimed_at.isoformat() if company.claimed_at else None,
                },
            )
        )

    return reminders


def _date_from_datetime(value: datetime | None, fallback: date) -> date:
    if value is None:
        return fallback
    if value.tzinfo is None:
        return value.date()
    return value.astimezone(UTC).date()
