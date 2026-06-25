from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateRead, TemplateUpdate

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateRead])
async def list_templates(
    template_type: str | None = None,
    tier: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Template]:
    stmt = select(Template).order_by(Template.created_at.desc())
    if template_type is not None:
        stmt = stmt.where(Template.template_type == template_type)
    if tier is not None:
        stmt = stmt.where(Template.tier == tier)
    result = await db.scalars(stmt)
    return list(result)


@router.post("", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> Template:
    if payload.created_by is not None:
        from app.models.user import User

        if await db.get(User, payload.created_by) is None:
            raise HTTPException(status_code=422, detail="User not found.")
    template = Template(**payload.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/{template_id}", response_model=TemplateRead)
async def get_template(template_id: UUID, db: AsyncSession = Depends(get_db)) -> Template:
    template = await db.get(Template, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    return template


@router.patch("/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: UUID,
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> Template:
    template = await db.get(Template, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")

    values = payload.model_dump(exclude_unset=True)
    if "created_by" in values and values["created_by"] is not None:
        from app.models.user import User

        if await db.get(User, values["created_by"]) is None:
            raise HTTPException(status_code=422, detail="User not found.")

    for field, value in values.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, db: AsyncSession = Depends(get_db)) -> Response:
    template = await db.get(Template, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")

    await db.delete(template)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
