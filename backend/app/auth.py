"""Shared-secret API key authentication.

Simple by design: this is a two-person tool (Julian + whoever hosts it), not
a multi-tenant product, so a single shared key checked on every request is
proportionate. Applied as a global FastAPI dependency in main.py so every
router is covered without touching each one individually — /health is the
only endpoint excluded (needed for container/uptime health checks).
"""
from fastapi import Header, HTTPException, status

from app.config import settings


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.api_key:
        # Fail closed: an unconfigured key means "not deployed securely yet",
        # not "allow everything". Forces the deployer to set a real key.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY no configurada en el servidor — ver .env.example",
        )
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente (header X-API-Key)",
        )
