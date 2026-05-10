from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discovery_candidate import DiscoveryCandidate
from app.models.job_posting import JobPosting


DEMO_DISCOVERY_ROWS = [
    {
        "company_name": "Northstar Robotics Demo",
        "domain": "northstar-robotics.demo.example",
        "careers_url": "https://northstar-robotics.demo.example/careers",
        "source": "demo_discovery",
        "source_url": "https://demo-discovery.demo.example/northstar-robotics",
        "detected_job_title": "Robotics Software Intern",
        "detected_job_url": "https://northstar-robotics.demo.example/jobs/robotics-software-intern",
        "country": "Canada",
        "region": "North America",
        "ats_type": "demo",
        "confidence_score": 0.86,
        "notes": "Fictional candidate created by demo-only discovery.",
    },
    {
        "company_name": "Aster Data Labs Demo",
        "domain": "aster-data-labs.demo.example",
        "careers_url": "https://aster-data-labs.demo.example/careers",
        "source": "demo_discovery",
        "source_url": "https://demo-discovery.demo.example/aster-data-labs",
        "detected_job_title": "Data Engineering Intern",
        "detected_job_url": "https://aster-data-labs.demo.example/jobs/data-engineering-intern",
        "country": "Germany",
        "region": "Europe",
        "ats_type": "demo",
        "confidence_score": 0.82,
        "notes": "Fictional candidate created by demo-only discovery.",
    },
    {
        "company_name": "Cobalt Climate Systems Demo",
        "domain": "cobalt-climate.demo.example",
        "careers_url": "https://cobalt-climate.demo.example/careers",
        "source": "demo_discovery",
        "source_url": "https://demo-discovery.demo.example/cobalt-climate",
        "detected_job_title": "Full Stack Intern",
        "detected_job_url": "https://cobalt-climate.demo.example/jobs/full-stack-intern",
        "country": "United Kingdom",
        "region": "Europe",
        "ats_type": "demo",
        "confidence_score": 0.79,
        "notes": "Fictional candidate created by demo-only discovery.",
    },
]


async def run_demo_discovery(db: AsyncSession) -> tuple[list[DiscoveryCandidate], int, int]:
    candidates_created = 0
    job_postings_created = 0
    candidates: list[DiscoveryCandidate] = []

    for row in DEMO_DISCOVERY_ROWS:
        candidate = await _get_existing_candidate(db, row["detected_job_url"])
        if candidate is None:
            candidate = DiscoveryCandidate(**row)
            db.add(candidate)
            candidates_created += 1
            await db.flush()
        candidates.append(candidate)

        job_posting = await _get_existing_job_posting(db, row["detected_job_url"])
        if job_posting is None:
            db.add(
                JobPosting(
                    title=row["detected_job_title"],
                    url=row["detected_job_url"],
                    location=row["country"],
                    remote=None,
                    description="Fictional demo posting. No external site was scraped.",
                    source=row["source"],
                )
            )
            job_postings_created += 1

    await db.commit()
    for candidate in candidates:
        await db.refresh(candidate)

    return candidates, candidates_created, job_postings_created


async def _get_existing_candidate(db: AsyncSession, detected_job_url: str) -> DiscoveryCandidate | None:
    result = await db.scalars(
        select(DiscoveryCandidate).where(DiscoveryCandidate.detected_job_url == detected_job_url)
    )
    return result.first()


async def _get_existing_job_posting(db: AsyncSession, url: str) -> JobPosting | None:
    result = await db.scalars(select(JobPosting).where(JobPosting.url == url))
    return result.first()
