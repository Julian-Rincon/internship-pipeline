from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.company import Company
from app.models.visa_data import VisaData
from app.schemas.visa_data import VisaDataCreate, VisaDataRead, VisaDataUpdate

router = APIRouter(prefix="/visa", tags=["visa"])


@router.get("", response_model=list[VisaDataRead])
async def list_visa_data(db: AsyncSession = Depends(get_db)) -> list[VisaData]:
    result = await db.scalars(select(VisaData).order_by(VisaData.created_at.desc()))
    return list(result)


@router.get("/by-company/{company_id}", response_model=list[VisaDataRead])
async def list_visa_by_company(company_id: UUID, db: AsyncSession = Depends(get_db)) -> list[VisaData]:
    result = await db.scalars(
        select(VisaData).where(VisaData.company_id == company_id).order_by(VisaData.created_at.desc())
    )
    return list(result)


@router.post("", response_model=VisaDataRead, status_code=status.HTTP_201_CREATED)
async def create_visa_data(
    payload: VisaDataCreate,
    db: AsyncSession = Depends(get_db),
) -> VisaData:
    if await db.get(Company, payload.company_id) is None:
        raise HTTPException(status_code=422, detail="Company not found.")
    visa = VisaData(**payload.model_dump())
    db.add(visa)
    await db.commit()
    await db.refresh(visa)
    return visa


@router.get("/{visa_id}", response_model=VisaDataRead)
async def get_visa_data(visa_id: UUID, db: AsyncSession = Depends(get_db)) -> VisaData:
    visa = await db.get(VisaData, visa_id)
    if visa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa data not found.")
    return visa


@router.patch("/{visa_id}", response_model=VisaDataRead)
async def update_visa_data(
    visa_id: UUID,
    payload: VisaDataUpdate,
    db: AsyncSession = Depends(get_db),
) -> VisaData:
    visa = await db.get(VisaData, visa_id)
    if visa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa data not found.")

    values = payload.model_dump(exclude_unset=True)
    if "company_id" in values:
        if await db.get(Company, values["company_id"]) is None:
            raise HTTPException(status_code=422, detail="Company not found.")

    for field, value in values.items():
        setattr(visa, field, value)

    await db.commit()
    await db.refresh(visa)
    return visa


@router.delete("/{visa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visa_data(visa_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    visa = await db.get(VisaData, visa_id)
    if visa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa data not found.")

    await db.delete(visa)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
