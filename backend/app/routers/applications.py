from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


async def validate_application_refs(
    db: AsyncSession,
    *,
    company_id: UUID,
    user_id: UUID,
    contact_id: UUID | None,
) -> None:
    if await db.get(Company, company_id) is None:
        raise HTTPException(status_code=422, detail="Company not found.")
    if await db.get(User, user_id) is None:
        raise HTTPException(status_code=422, detail="User not found.")
    if contact_id is not None:
        contact = await db.get(Contact, contact_id)
        if contact is None:
            raise HTTPException(status_code=422, detail="Contact not found.")
        if contact.company_id != company_id:
            raise HTTPException(status_code=422, detail="Contact does not belong to application company.")


@router.get("", response_model=list[ApplicationRead])
async def list_applications(db: AsyncSession = Depends(get_db)) -> list[Application]:
    result = await db.scalars(select(Application).order_by(Application.created_at.desc()))
    return list(result)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
) -> Application:
    await validate_application_refs(
        db,
        company_id=payload.company_id,
        user_id=payload.user_id,
        contact_id=payload.contact_id,
    )
    application = Application(**payload.model_dump())
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(application_id: UUID, db: AsyncSession = Depends(get_db)) -> Application:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    return application


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: UUID,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
) -> Application:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    values = payload.model_dump(exclude_unset=True)
    next_company_id = values.get("company_id", application.company_id)
    next_user_id = values.get("user_id", application.user_id)
    next_contact_id = values.get("contact_id", application.contact_id)
    await validate_application_refs(
        db,
        company_id=next_company_id,
        user_id=next_user_id,
        contact_id=next_contact_id,
    )

    for field, value in values.items():
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    await db.delete(application)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

