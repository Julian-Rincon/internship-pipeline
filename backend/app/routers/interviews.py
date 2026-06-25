from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.company import Company
from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewRead, InterviewUpdate

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def validate_interview_refs(
    db: AsyncSession,
    *,
    company_id: UUID,
    user_id: UUID,
) -> None:
    if await db.get(Company, company_id) is None:
        raise HTTPException(status_code=422, detail="Company not found.")
    if await db.get(User, user_id) is None:
        raise HTTPException(status_code=422, detail="User not found.")


@router.get("", response_model=list[InterviewRead])
async def list_interviews(
    company_id: UUID | None = None,
    user_id: UUID | None = None,
    outcome: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Interview]:
    query = select(Interview).order_by(Interview.created_at.desc())
    if company_id is not None:
        query = query.where(Interview.company_id == company_id)
    if user_id is not None:
        query = query.where(Interview.user_id == user_id)
    if outcome is not None:
        query = query.where(Interview.outcome == outcome)
    result = await db.scalars(query)
    return list(result)


@router.post("", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreate,
    db: AsyncSession = Depends(get_db),
) -> Interview:
    await validate_interview_refs(db, company_id=payload.company_id, user_id=payload.user_id)
    interview = Interview(**payload.model_dump())
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/{interview_id}", response_model=InterviewRead)
async def get_interview(interview_id: UUID, db: AsyncSession = Depends(get_db)) -> Interview:
    interview = await db.get(Interview, interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")
    return interview


@router.patch("/{interview_id}", response_model=InterviewRead)
async def update_interview(
    interview_id: UUID,
    payload: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
) -> Interview:
    interview = await db.get(Interview, interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")

    values = payload.model_dump(exclude_unset=True)
    next_company_id = values.get("company_id", interview.company_id)
    next_user_id = values.get("user_id", interview.user_id)
    await validate_interview_refs(db, company_id=next_company_id, user_id=next_user_id)

    for field, value in values.items():
        setattr(interview, field, value)

    await db.commit()
    await db.refresh(interview)
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(interview_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    interview = await db.get(Interview, interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")

    await db.delete(interview)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
