from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discovery_candidate import DiscoveryCandidate
from app.models.discovery_source import DiscoverySource
from app.models.job_posting import JobPosting
from app.schemas.discovery import DiscoverySourceRunResult

INTERNSHIP_TITLE_KEYWORDS = (
    "intern",
    "internship",
    "trainee",
    "graduate",
    "new grad",
    "junior",
    "entry level",
    "student",
    "co-op",
    "apprenticeship",
)
MAX_ITEMS_PER_SOURCE = 50
ATS_USER_AGENT = "internship-pipeline-ats-intake/0.7 local-dev"
REQUEST_TIMEOUT_SECONDS = 10.0


@dataclass
class ParsedJob:
    title: str
    url: str
    location: str | None
    remote: bool | None
    description: str | None


def build_source_url(source: DiscoverySource) -> str:
    if source.base_url:
        return source.base_url
    if source.source_type == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{source.source_key}/jobs?content=true"
    if source.source_type == "lever":
        return f"https://api.lever.co/v0/postings/{source.source_key}?mode=json"
    return (
        "https://api.ashbyhq.com/posting-api/job-board/"
        f"{source.source_key}?includeCompensation=false"
    )


async def fetch_json(url: str) -> Any:
    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": ATS_USER_AGENT, "Accept": "application/json"},
        follow_redirects=False,
    ) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise ValueError(f"ATS endpoint returned HTTP {response.status_code}.")
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("ATS endpoint did not return valid JSON.") from exc


async def run_discovery_source(db: AsyncSession, source: DiscoverySource) -> DiscoverySourceRunResult:
    if not source.enabled:
        raise ValueError("Discovery source is disabled.")

    if source.source_type == "getonboard":
        from app.discovery.runners.getonboard_runner import run_getonboard_discovery

        now = datetime.now(UTC)
        try:
            created = await run_getonboard_discovery(db)
            source.last_status = "success"
            source.last_error = None
        except Exception as exc:
            created = 0
            source.last_status = "error"
            source.last_error = str(exc)
        source.last_run_at = now
        await db.commit()
        await db.refresh(source)
        return DiscoverySourceRunResult(
            source_id=source.id,
            source_name=source.name,
            fetched_count=created,
            internship_like_count=created,
            candidates_created=created,
            candidates_skipped=0,
            job_postings_created=0,
            errors=[source.last_error] if source.last_error else [],
        )

    source_url = build_source_url(source)
    now = datetime.now(UTC)
    errors: list[str] = []
    fetched_count = 0
    internship_like_count = 0
    candidates_created = 0
    candidates_skipped = 0
    job_postings_created = 0

    try:
        payload = await fetch_json(source_url)
        jobs = parse_jobs(source, payload)[:MAX_ITEMS_PER_SOURCE]
        fetched_count = len(jobs)

        for job in jobs:
            if not is_internship_like(job.title):
                continue
            internship_like_count += 1

            existing_job = await _get_job_posting_by_url(db, job.url)
            if existing_job is None:
                db.add(
                    JobPosting(
                        title=job.title,
                        url=job.url,
                        location=job.location,
                        remote=job.remote,
                        description=job.description,
                        source=f"ats:{source.source_type}",
                        status="open",
                    )
                )
                job_postings_created += 1

            existing_candidate = await _get_candidate_by_job_url(db, job.url)
            if existing_candidate is not None:
                candidates_skipped += 1
                continue

            db.add(
                DiscoveryCandidate(
                    company_name=source.company_hint or source.name,
                    domain=infer_domain(source),
                    careers_url=source_url,
                    source=f"ats:{source.source_type}",
                    source_url=source_url,
                    detected_job_title=job.title,
                    detected_job_url=job.url,
                    country=source.country,
                    region=source.region,
                    ats_type=source.source_type,
                    confidence_score=0.74,
                    status="pending_review",
                    notes="Created from controlled public ATS source intake. Requires human review.",
                )
            )
            candidates_created += 1

        source.last_status = "success"
        source.last_error = None
    except Exception as exc:
        errors.append(str(exc))
        source.last_status = "error"
        source.last_error = str(exc)

    source.last_run_at = now
    await db.commit()
    await db.refresh(source)

    return DiscoverySourceRunResult(
        source_id=source.id,
        source_name=source.name,
        fetched_count=fetched_count,
        internship_like_count=internship_like_count,
        candidates_created=candidates_created,
        candidates_skipped=candidates_skipped,
        job_postings_created=job_postings_created,
        errors=errors,
    )


def parse_jobs(source: DiscoverySource, payload: Any) -> list[ParsedJob]:
    if source.source_type == "greenhouse":
        return parse_greenhouse_jobs(payload)
    if source.source_type == "lever":
        return parse_lever_jobs(payload)
    return parse_ashby_jobs(payload)


def parse_greenhouse_jobs(payload: Any) -> list[ParsedJob]:
    rows = payload.get("jobs", []) if isinstance(payload, dict) else []
    jobs: list[ParsedJob] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = row.get("title")
        url = row.get("absolute_url") or row.get("url")
        if not title or not url:
            continue
        location = row.get("location") if isinstance(row.get("location"), dict) else {}
        jobs.append(
            ParsedJob(
                title=title,
                url=url,
                location=location.get("name"),
                remote=_detect_remote(location.get("name")),
                description=_clean_description(row.get("content")),
            )
        )
    return jobs


def parse_lever_jobs(payload: Any) -> list[ParsedJob]:
    rows = payload if isinstance(payload, list) else []
    jobs: list[ParsedJob] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = row.get("text")
        url = row.get("hostedUrl") or row.get("applyUrl")
        if not title or not url:
            continue
        categories = row.get("categories") if isinstance(row.get("categories"), dict) else {}
        location = categories.get("location")
        workplace_type = categories.get("commitment") or row.get("workplaceType")
        jobs.append(
            ParsedJob(
                title=title,
                url=url,
                location=location,
                remote=_detect_remote(" ".join([str(location or ""), str(workplace_type or "")])),
                description=_clean_description(row.get("descriptionPlain") or row.get("description")),
            )
        )
    return jobs


def parse_ashby_jobs(payload: Any) -> list[ParsedJob]:
    rows = payload.get("jobs", []) if isinstance(payload, dict) else []
    jobs: list[ParsedJob] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = row.get("title")
        url = row.get("jobUrl") or row.get("url")
        if not title or not url:
            continue
        location = row.get("location")
        jobs.append(
            ParsedJob(
                title=title,
                url=url,
                location=location,
                remote=row.get("isRemote") if isinstance(row.get("isRemote"), bool) else _detect_remote(location),
                description=_clean_description(row.get("descriptionPlain") or row.get("descriptionHtml")),
            )
        )
    return jobs


def is_internship_like(title: str) -> bool:
    normalized = title.lower()
    return any(keyword in normalized for keyword in INTERNSHIP_TITLE_KEYWORDS)


def infer_domain(source: DiscoverySource) -> str | None:
    if not source.base_url:
        return None
    parsed = urlparse(source.base_url)
    hostname = parsed.hostname
    if not hostname:
        return None
    return hostname.removeprefix("www.")


def _detect_remote(value: str | None) -> bool | None:
    if not value:
        return None
    return "remote" in value.lower()


def _clean_description(value: str | None) -> str | None:
    if not value:
        return None
    return unescape(value).replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")


async def _get_job_posting_by_url(db: AsyncSession, url: str) -> JobPosting | None:
    result = await db.scalars(select(JobPosting).where(JobPosting.url == url))
    return result.first()


async def _get_candidate_by_job_url(db: AsyncSession, url: str) -> DiscoveryCandidate | None:
    result = await db.scalars(
        select(DiscoveryCandidate).where(DiscoveryCandidate.detected_job_url == url)
    )
    return result.first()
