from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.company import Company
from app.models.discovery_candidate import DiscoveryCandidate
from app.models.job_posting import JobPosting
from app.schemas.company import CompanyRead
from app.schemas.discovery import (
    DemoDiscoveryResult,
    DiscoveryCandidateRead,
    DiscoveryCandidateUpdate,
    JobPostingRead,
)
from app.services.discovery import run_demo_discovery

discovery_router = APIRouter(prefix="/discovery-candidates", tags=["discovery"])
job_postings_router = APIRouter(prefix="/job-postings", tags=["job-postings"])


@job_postings_router.get("", response_model=list[JobPostingRead])
async def list_job_postings(db: AsyncSession = Depends(get_db)) -> list[JobPosting]:
    result = await db.scalars(select(JobPosting).order_by(JobPosting.detected_at.desc()))
    return list(result)


@job_postings_router.get("/{job_posting_id}", response_model=JobPostingRead)
async def get_job_posting(job_posting_id: UUID, db: AsyncSession = Depends(get_db)) -> JobPosting:
    job_posting = await db.get(JobPosting, job_posting_id)
    if job_posting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    return job_posting


@discovery_router.get("", response_model=list[DiscoveryCandidateRead])
async def list_discovery_candidates(db: AsyncSession = Depends(get_db)) -> list[DiscoveryCandidate]:
    result = await db.scalars(select(DiscoveryCandidate).order_by(DiscoveryCandidate.created_at.desc()))
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
