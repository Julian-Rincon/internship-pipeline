from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.discovery_source import DiscoverySource
from app.schemas.discovery import (
    DiscoverySourceCreate,
    DiscoverySourceRead,
    DiscoverySourceRunResult,
    DiscoverySourceUpdate,
)
from app.services.ats_sources import run_discovery_source

router = APIRouter(prefix="/discovery-sources", tags=["discovery-sources"])


@router.get("", response_model=list[DiscoverySourceRead])
async def list_discovery_sources(db: AsyncSession = Depends(get_db)) -> list[DiscoverySource]:
    result = await db.scalars(select(DiscoverySource).order_by(DiscoverySource.created_at.desc()))
    return list(result)


@router.post("", response_model=DiscoverySourceRead, status_code=status.HTTP_201_CREATED)
async def create_discovery_source(
    payload: DiscoverySourceCreate,
    db: AsyncSession = Depends(get_db),
) -> DiscoverySource:
    source = DiscoverySource(**payload.model_dump())
    db.add(source)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A discovery source with that type and key already exists.",
        ) from exc

    await db.refresh(source)
    return source


@router.post("/run-enabled", response_model=list[DiscoverySourceRunResult])
async def run_enabled_discovery_sources(
    db: AsyncSession = Depends(get_db),
) -> list[DiscoverySourceRunResult]:
    result = await db.scalars(
        select(DiscoverySource).where(DiscoverySource.enabled.is_(True)).order_by(DiscoverySource.created_at.asc())
    )
    outputs: list[DiscoverySourceRunResult] = []
    for source in result:
        outputs.append(await run_discovery_source(db, source))
    return outputs


@router.get("/{source_id}", response_model=DiscoverySourceRead)
async def get_discovery_source(source_id: UUID, db: AsyncSession = Depends(get_db)) -> DiscoverySource:
    source = await db.get(DiscoverySource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery source not found.")
    return source


@router.patch("/{source_id}", response_model=DiscoverySourceRead)
async def update_discovery_source(
    source_id: UUID,
    payload: DiscoverySourceUpdate,
    db: AsyncSession = Depends(get_db),
) -> DiscoverySource:
    source = await db.get(DiscoverySource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery source not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, field, value)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A discovery source with that type and key already exists.",
        ) from exc

    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discovery_source(source_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    source = await db.get(DiscoverySource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery source not found.")

    await db.delete(source)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{source_id}/run", response_model=DiscoverySourceRunResult)
async def run_single_discovery_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DiscoverySourceRunResult:
    source = await db.get(DiscoverySource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery source not found.")
    if not source.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discovery source is disabled.")

    return await run_discovery_source(db, source)
