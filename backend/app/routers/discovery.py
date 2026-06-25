from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.discovery_candidate import DiscoveryCandidate
from app.models.job_posting import JobPosting
from app.models.user import User
from app.schemas.application import ApplicationRead
from app.schemas.company import CompanyRead
from app.schemas.discovery import (
    DemoDiscoveryResult,
    DiscoveryCandidateRead,
    DiscoveryCandidateUpdate,
    JobPostingApplicationCreate,
    JobPostingCompanyLink,
    JobPostingRead,
)
from app.services.discovery import run_demo_discovery

discovery_router = APIRouter(prefix="/discovery-candidates", tags=["discovery"])
job_postings_router = APIRouter(prefix="/job-postings", tags=["job-postings"])


@job_postings_router.get("", response_model=list[JobPostingRead])
async def list_job_postings(
    status_filter: str | None = Query(default=None, alias="status"),
    source: str | None = None,
    company_id: UUID | None = None,
    title: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[JobPosting]:
    statement = select(JobPosting)
    if status_filter:
        statement = statement.where(JobPosting.status == status_filter)
    if source:
        statement = statement.where(JobPosting.source == source)
    if company_id:
        statement = statement.where(JobPosting.company_id == company_id)
    if title:
        statement = statement.where(JobPosting.title.ilike(f"%{title}%"))

    result = await db.scalars(statement.order_by(JobPosting.detected_at.desc()))
    return list(result)


@job_postings_router.get("/{job_posting_id}", response_model=JobPostingRead)
async def get_job_posting(job_posting_id: UUID, db: AsyncSession = Depends(get_db)) -> JobPosting:
    job_posting = await db.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    return job_posting


@job_postings_router.patch("/{job_posting_id}/link-company", response_model=JobPostingRead)
async def link_job_posting_company(
    job_posting_id: UUID,
    payload: JobPostingCompanyLink,
    db: AsyncSession = Depends(get_db),
) -> JobPosting:
    job_posting = await db.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    if await db.get(Company, payload.company_id) is None:
        raise HTTPException(status_code=422, detail="Company not found.")

    job_posting.company_id = payload.company_id
    await db.commit()
    await db.refresh(job_posting)
    return job_posting


@job_postings_router.post("/{job_posting_id}/create-application", response_model=ApplicationRead)
async def create_application_from_job_posting(
    job_posting_id: UUID,
    payload: JobPostingApplicationCreate,
    db: AsyncSession = Depends(get_db),
) -> Application:
    job_posting = await db.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    company_id = job_posting.company_id
    if company_id is None:
        raise HTTPException(
            status_code=422,
            detail="Job posting must be linked to an approved company before creating an application.",
        )

    if await db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=422, detail="User not found.")

    if payload.contact_id is not None:
        contact = await db.get(Contact, payload.contact_id)
        if contact is None:
            raise HTTPException(status_code=422, detail="Contact not found.")
        if contact.company_id != company_id:
            raise HTTPException(status_code=422, detail="Contact does not belong to application company.")

    application = Application(
        company_id=company_id,
        user_id=payload.user_id,
        contact_id=payload.contact_id,
        type=payload.type,
        status=payload.status,
        next_action=payload.next_action,
        next_action_due=payload.next_action_due,
        notes=_job_application_notes(job_posting, payload.notes),
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@discovery_router.get("", response_model=list[DiscoveryCandidateRead])
async def list_discovery_candidates(
    status_filter: str | None = Query(default=None, alias="status"),
    created_since: datetime | None = Query(default=None, description="ISO-8601 timestamp — only candidates created after this time"),
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[DiscoveryCandidate]:
    statement = select(DiscoveryCandidate)
    if status_filter:
        statement = statement.where(DiscoveryCandidate.status == status_filter)
    if created_since:
        statement = statement.where(DiscoveryCandidate.created_at >= created_since)
    result = await db.scalars(statement.order_by(DiscoveryCandidate.created_at.desc()).limit(limit))
    return list(result)


@discovery_router.post("/run-demo-discovery", response_model=DemoDiscoveryResult)
async def run_demo_discovery_endpoint(db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    candidates, candidates_created, job_postings_created = await run_demo_discovery(db)
    return {
        "candidates_created": candidates_created,
        "job_postings_created": job_postings_created,
        "candidates": candidates,
    }


@discovery_router.get("/{candidate_id}", response_model=DiscoveryCandidateRead)
async def get_discovery_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DiscoveryCandidate:
    candidate = await db.get(DiscoveryCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery candidate not found.")
    return candidate


@discovery_router.patch("/{candidate_id}", response_model=DiscoveryCandidateRead)
async def update_discovery_candidate(
    candidate_id: UUID,
    payload: DiscoveryCandidateUpdate,
    db: AsyncSession = Depends(get_db),
) -> DiscoveryCandidate:
    candidate = await db.get(DiscoveryCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery candidate not found.")

    values = payload.model_dump(exclude_unset=True)
    if values.get("status") in {"approved", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use the approve or reject endpoint to review a discovery candidate.",
        )

    for field, value in values.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)
    return candidate


@discovery_router.post("/{candidate_id}/approve", response_model=CompanyRead)
async def approve_discovery_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Company:
    candidate = await db.get(DiscoveryCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery candidate not found.")

    company = await _find_existing_company(db, candidate)
    if company is None:
        company = Company(
            name=candidate.company_name,
            domain=candidate.domain,
            country=candidate.country,
            region=candidate.region,
            careers_url=candidate.careers_url,
            ats_type=candidate.ats_type,
            visa_friendly_intern="unknown",
            status="active",
        )
        db.add(company)
        await db.flush()

    candidate.status = "approved"
    candidate.reviewed_at = datetime.now(UTC)
    await _link_detected_job_posting(db, candidate, company)
    await db.commit()
    await db.refresh(company)
    return company


@discovery_router.post("/{candidate_id}/reject", response_model=DiscoveryCandidateRead)
async def reject_discovery_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DiscoveryCandidate:
    candidate = await db.get(DiscoveryCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery candidate not found.")

    candidate.status = "rejected"
    candidate.reviewed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(candidate)
    return candidate


async def _find_existing_company(db: AsyncSession, candidate: DiscoveryCandidate) -> Company | None:
    if candidate.domain:
        result = await db.scalars(select(Company).where(Company.domain == candidate.domain))
        company = result.first()
        if company is not None:
            return company

    normalized_name = _normalize_company_name(candidate.company_name)
    result = await db.scalars(
        select(Company).where(func.lower(func.trim(Company.name)) == normalized_name)
    )
    return result.first()


def _normalize_company_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


async def _link_detected_job_posting(
    db: AsyncSession,
    candidate: DiscoveryCandidate,
    company: Company,
) -> None:
    if not candidate.detected_job_url:
        return

    result = await db.scalars(select(JobPosting).where(JobPosting.url == candidate.detected_job_url))
    job_posting = result.first()
    if job_posting is not None and job_posting.company_id is None:
        job_posting.company_id = company.id


def _job_application_notes(job_posting: JobPosting, notes: str | None) -> str:
    job_context = f"Job posting: {job_posting.title}\nURL: {job_posting.url}"
    if notes:
        return f"{notes}\n\n{job_context}"
    return job_context
