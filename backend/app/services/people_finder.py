import logging
import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.contact import Contact

logger = logging.getLogger(__name__)


async def get_ranked_contacts(company_id: UUID, db: AsyncSession) -> list[Contact]:
    """
    Return contacts for the given company ordered by total_score DESC,
    affinity_score DESC (nulls last).
    """
    result = await db.scalars(
        select(Contact)
        .where(Contact.company_id == company_id)
        .order_by(
            Contact.total_score.desc().nulls_last(),
            Contact.affinity_score.desc().nulls_last(),
        )
    )
    return list(result)


async def enrich_contact_scores(contact_id: UUID, db: AsyncSession) -> Contact:
    """
    Simulate contact enrichment by assigning realistic random scores.

    If the contact already has total_score >= 50, returns it as-is.
    Otherwise assigns affinity_score (20-80), role_relevance (30-90),
    and computes total_score = affinity_score * 0.5 + role_relevance * 0.3 + 20.

    Logs a reminder that real enrichment requires API keys.
    """
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise ValueError(f"Contact {contact_id} not found")

    if contact.total_score is not None and contact.total_score >= 50:
        return contact

    affinity_score = random.randint(20, 80)
    role_relevance = random.randint(30, 90)
    total_score = int(affinity_score * 0.5 + role_relevance * 0.3 + 20)
    # Clamp to 100
    total_score = min(total_score, 100)

    contact.affinity_score = affinity_score
    contact.role_relevance = role_relevance
    contact.total_score = total_score

    await db.commit()
    await db.refresh(contact)

    logger.info(
        "Simulated enrichment for contact %s. Real enrichment needs API keys.",
        contact_id,
    )
    return contact


async def run_people_finder(company_id: UUID, db: AsyncSession) -> dict:
    """
    Orchestrate the people-finder process for a company.

    - If >= 5 contacts already have total_score set, return early with status "ok".
    - Otherwise enrich contacts that are missing scores and return status "enriched".
    """
    company = await db.get(Company, company_id)
    if company is None:
        raise ValueError(f"Company {company_id} not found")

    contacts = await get_ranked_contacts(company_id, db)

    scored = [c for c in contacts if c.total_score is not None]
    if len(scored) >= 5:
        return {
            "status": "ok",
            "count": len(scored),
            "message": f"Company already has {len(scored)} scored contacts.",
        }

    unscored = [c for c in contacts if c.total_score is None]
    enriched_count = 0
    for contact in unscored:
        await enrich_contact_scores(contact.id, db)
        enriched_count += 1

    return {
        "status": "enriched",
        "count": enriched_count,
        "message": (
            f"Enriched {enriched_count} contact(s) with simulated scores. "
            "Set GITHUB_TOKEN, APOLLO_API_KEY, or APIFY_API_TOKEN for real enrichment."
        ),
    }
