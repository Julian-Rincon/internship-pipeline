from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


async def ensure_company_exists(company_id: UUID, db: AsyncSession) -> None:
    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=422, detail="Company not found.")


def contact_values(payload: ContactCreate | ContactUpdate, *, exclude_unset: bool = False) -> dict:
    values = payload.model_dump(exclude_unset=exclude_unset)
    if "metadata" in values:
        values["contact_metadata"] = values.pop("metadata")
    return values


@router.get("", response_model=list[ContactRead])
async def list_contacts(db: AsyncSession = Depends(get_db)) -> list[Contact]:
    result = await db.scalars(select(Contact).order_by(Contact.created_at.desc()))
    return list(result)


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)) -> Contact:
    await ensure_company_exists(payload.company_id, db)
    contact = Contact(**contact_values(payload))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(contact_id: UUID, db: AsyncSession = Depends(get_db)) -> Contact:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    values = contact_values(payload, exclude_unset=True)
    if "company_id" in values:
        await ensure_company_exists(values["company_id"], db)

    for field, value in values.items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    contact = await db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    await db.delete(contact)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
