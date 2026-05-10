from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.user import User
from app.schemas.application import ApplicationRead
from app.schemas.company import CompanyClaim, CompanyCreate, CompanyOwnershipUpdate, CompanyRead, CompanyUpdate
from app.schemas.contact import ContactRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
async def list_companies(db: AsyncSession = Depends(get_db)) -> list[Company]:
    result = await db.scalars(select(Company).order_by(Company.created_at.desc()))
    return list(result)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with that domain already exists.",
        ) from exc

    await db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: UUID, db: AsyncSession = Depends(get_db)) -> Company:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company


@router.get("/{company_id}/contacts", response_model=list[ContactRead])
async def list_company_contacts(company_id: UUID, db: AsyncSession = Depends(get_db)) -> list[Contact]:
    if await db.get(Company, company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    result = await db.scalars(
        select(Contact)
        .where(Contact.company_id == company_id)
        .order_by(Contact.created_at.desc())
    )
    return list(result)


@router.get("/{company_id}/applications", response_model=list[ApplicationRead])
async def list_company_applications(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Application]:
    if await db.get(Company, company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    result = await db.scalars(
        select(Application)
        .where(Application.company_id == company_id)
        .order_by(Application.created_at.desc())
    )
    return list(result)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
) -> Company:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with that domain already exists.",
        ) from exc

    await db.refresh(company)
    return company


@router.post("/{company_id}/claim", response_model=CompanyRead)
async def claim_company(
    company_id: UUID,
    payload: CompanyClaim,
    db: AsyncSession = Depends(get_db),
) -> Company:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    if await db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=422, detail="User not found.")

    if company.owner_user_id is not None and company.owner_user_id != payload.user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company is already claimed by another user.",
        )

    if company.owner_user_id == payload.user_id:
        company.ownership_status = "claimed"
        if payload.ownership_notes is not None:
            company.ownership_notes = payload.ownership_notes
        if company.claimed_at is None:
            company.claimed_at = datetime.now(UTC)
    else:
        company.owner_user_id = payload.user_id
        company.ownership_status = "claimed"
        company.claimed_at = datetime.now(UTC)
        if payload.ownership_notes is not None:
            company.ownership_notes = payload.ownership_notes

    await db.commit()
    await db.refresh(company)
    return company


@router.post("/{company_id}/release", response_model=CompanyRead)
async def release_company(company_id: UUID, db: AsyncSession = Depends(get_db)) -> Company:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    company.owner_user_id = None
    company.ownership_status = "unclaimed"
    company.claimed_at = None
    company.ownership_notes = None

    await db.commit()
    await db.refresh(company)
    return company


@router.patch("/{company_id}/ownership", response_model=CompanyRead)
async def update_company_ownership(
    company_id: UUID,
    payload: CompanyOwnershipUpdate,
    db: AsyncSession = Depends(get_db),
) -> Company:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    values = payload.model_dump(exclude_unset=True)
    next_status = values.get("ownership_status", company.ownership_status)

    if next_status == "claimed" and company.owner_user_id is None:
        raise HTTPException(
            status_code=422,
            detail="Cannot mark company as claimed without an owner.",
        )

    if next_status in {"paused", "done"} and company.owner_user_id is None:
        raise HTTPException(
            status_code=422,
            detail="Cannot update ownership status without an owner.",
        )

    for field, value in values.items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    await db.delete(company)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
