"""Two-tier authentication.

- JWT (Authorization: Bearer <token>) identifies a real PERSON — issued by
  POST /auth/login after checking their password. Now that the team is
  ~5-6 people, knowing WHO did what (not just "someone with the shared
  secret") is worth the extra piece.
- The shared API key (X-API-Key) still exists for SYSTEM callers that
  aren't a person: n8n's scheduled workflows and the frontend's own
  server-side rendering. Forcing a cron job to "log in" as a fake user
  doesn't map to reality — a service credential is the right tool there.

require_auth() accepts EITHER and is applied globally to every router
except /health and /auth/*. Both credentials fail closed: an unconfigured
secret refuses every request rather than silently allowing everything.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status

from app.config import settings

_JWT_ALGORITHM = "HS256"


# ── Passwords ──────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Malformed/legacy hash — never crash the login attempt over it.
        return False


# ── JWT ──────────────────────────────────────────────────────────────────────

def create_access_token(*, user_id: str, role: str) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET no configurado en el servidor — ver .env.example")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expires_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_JWT_ALGORITHM)


def _decode_token(token: str) -> dict | None:
    if not settings.jwt_secret:
        return None
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


# ── FastAPI dependencies ─────────────────────────────────────────────────────

async def get_current_user(authorization: str | None = Header(default=None)) -> dict | None:
    """Decoded JWT payload ({"sub": user_id, "role": ...}) if a valid bearer
    token is present, else None. Never raises — require_auth() decides what
    "no user" means for a given route."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return _decode_token(authorization.removeprefix("Bearer ").strip())


async def _service_key_ok(x_api_key: str | None = Header(default=None)) -> bool:
    return bool(settings.api_key) and x_api_key == settings.api_key


async def require_auth(
    user: dict | None = Depends(get_current_user),
    service_ok: bool = Depends(_service_key_ok),
) -> dict | None:
    """Global auth dependency: a valid JWT OR the service API key. Returns
    the JWT payload when the caller is a real logged-in person, or None when
    the caller authenticated as a system (n8n, SSR) — routes that need to
    know "who" can check for a non-None return; most don't need to."""
    if user is not None:
        return user
    if service_ok:
        return None
    if not settings.jwt_secret and not settings.api_key:
        # Nothing configured at all — fail closed, not open.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ni JWT_SECRET ni API_KEY configurados en el servidor — ver .env.example",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida: Authorization: Bearer <token> o X-API-Key",
    )


async def require_admin(auth: dict | None = Depends(require_auth)) -> dict | None:
    """Stricter than require_auth: for account management (create/delete a
    user). A service-key caller (auth is None) is trusted like before — it's
    the human JWT case that now must carry role=admin."""
    if auth is not None and auth.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol admin para esta acción.",
        )
    return auth
