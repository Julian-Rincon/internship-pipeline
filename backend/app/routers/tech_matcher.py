from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.contact import ContactRead
from app.services.people_finder import run_people_finder
from app.services.tech_matcher import match_users_to_company

router = APIRouter(tags=["tech-matcher"])


@router.get("/companies/{company_id}/tech-match")
async def get_tech_match(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Return users ranked by how well their skills match the company's inferred tech stack.
    """
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return await match_users_to_company(company_id, db)


@router.get("/companies/{company_id}/contacts/ranked", response_model=list[ContactRead])
async def get_ranked_contacts(
    company_id: UUID,
    contacted: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Contact]:
    """
    Return contacts for the given company ordered by total_score DESC, affinity_score DESC.
    Optionally filter by ?contacted=true/false.
    """
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    query = (
        select(Contact)
        .where(Contact.company_id == company_id)
        .order_by(
            Contact.total_score.desc().nulls_last(),
            Contact.affinity_score.desc().nulls_last(),
        )
    )

    if contacted is not None:
        query = query.where(Contact.contacted == contacted)

    result = await db.scalars(query)
    return list(result)


@router.post("/companies/{company_id}/enrich-contacts")
async def enrich_contacts(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Run the people-finder enrichment pipeline for a company's contacts.
    Simulates enrichment scores when real API keys are not configured.
    """
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return await run_people_finder(company_id, db)
