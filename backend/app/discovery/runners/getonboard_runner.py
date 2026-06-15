"""
GetOnBoard public search API runner.

Fetches internship/junior postings and creates DiscoveryCandidate records.
No authentication required — controlled GET only.

Usage:
    result = await run_getonboard_discovery(db)
    print(f"Created {result} candidates")
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discovery_candidate import DiscoveryCandidate

GETONBOARD_URL = "https://www.getonbrd.com/api/v0/search/jobs"
GETONBOARD_SOURCE_TAG = "getonboard"

INTERNSHIP_KEYWORDS = [
    "data science",
    "machine learning",
    "data engineer",
    "AI",
    "python developer",
    "practicante",
    "internship",
    "trainee",
    "junior data",
]

REQUEST_TIMEOUT = 15.0
MAX_PER_KEYWORD = 10


async def run_getonboard_discovery(db: AsyncSession) -> int:
    """Fetch GetOnBoard postings and insert new DiscoveryCandidates. Returns count created."""
    created = 0

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for keyword in INTERNSHIP_KEYWORDS:
            try:
                resp = await client.get(
                    GETONBOARD_URL,
                    params={"query": keyword, "per_page": MAX_PER_KEYWORD, "remote": True},
                    headers={"Accept": "application/json"},
                )
            except httpx.RequestError as exc:
                print(f"[getonboard] Network error for '{keyword}': {exc}")
                continue

            if not resp.is_success:
                print(f"[getonboard] HTTP {resp.status_code} for '{keyword}'")
                continue

            try:
                jobs = resp.json().get("data", [])
            except ValueError:
                continue

            for job in jobs[:MAX_PER_KEYWORD]:
                attrs = job.get("attributes", {})
                title = attrs.get("title", "").strip()
                company = attrs.get("company_name", "").strip()
                url = attrs.get("url", "").strip()

                if not (title and url):
                    continue

                existing = await db.scalar(
                    select(DiscoveryCandidate).where(DiscoveryCandidate.detected_job_url == url)
                )
                if existing is not None:
                    continue

                db.add(
                    DiscoveryCandidate(
                        company_name=company or "GetOnBoard listing",
                        source=GETONBOARD_SOURCE_TAG,
                        source_url=GETONBOARD_URL,
                        detected_job_title=title,
                        detected_job_url=url,
                        confidence_score=0.65,
                        status="pending_review",
                        notes=f"Found via GetOnBoard search: '{keyword}'",
                    )
                )
                created += 1

    await db.commit()
    return created
