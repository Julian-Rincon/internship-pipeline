from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, verify_password
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.scalars(select(User).where(User.email == payload.email))
    user = result.first()

    # Same error for "no such user" and "wrong password" — don't leak which
    # emails have accounts.
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email o contraseña incorrectos.",
    )
    if user is None or not user.hashed_password:
        raise invalid
    if not verify_password(payload.password, user.hashed_password):
        raise invalid

    token = create_access_token(user_id=str(user.id), role=user.role)
    return TokenResponse(access_token=token, expires_in_seconds=settings.jwt_expires_seconds)
