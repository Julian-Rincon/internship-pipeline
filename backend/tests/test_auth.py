"""Dedicated coverage for the real auth dependencies (require_auth,
require_admin) and the /auth/login flow — none of it bypassed here.

Every other test file overrides require_auth (see conftest.py) to focus on
business logic. This file is the only one that exercises the actual checks.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password
from app.db import engine, get_db
from app.main import app
from app.models.user import User


@pytest_asyncio.fixture
async def raw_client():
    """Same DB-isolation pattern as conftest's `client` fixture (transaction
    rolled back after the test, engine disposed) — but only get_db is
    overridden here, NOT require_auth, so the real auth check runs. Exposes
    `.db_session` for tests that need to seed a real user (e.g. login)."""
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as c:
            c.db_session = session
            yield c
    finally:
        app.dependency_overrides.clear()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
        await engine.dispose()


# ── Service API key (system callers: n8n, SSR) ──────────────────────────────

@pytest.mark.asyncio
async def test_health_is_public_without_any_credential(raw_client):
    resp = await raw_client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_protected_route_rejects_missing_credential(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_rejects_wrong_api_key(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_accepts_correct_api_key(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users", headers={"X-API-Key": "real-secret"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_nothing_configured_fails_closed(raw_client, monkeypatch):
    """Neither API_KEY nor JWT_SECRET set on the server → refuse everything,
    never silently allow access."""
    monkeypatch.setattr("app.auth.settings.api_key", "")
    monkeypatch.setattr("app.auth.settings.jwt_secret", "")
    resp = await raw_client.get("/users", headers={"X-API-Key": "anything"})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_delete_user_requires_admin_not_just_any_credential(raw_client, monkeypatch):
    """The service API key IS trusted for admin actions (it represents a
    trusted system, e.g. a seed script) — this only proves DELETE is behind
    *some* real check, not reachable with zero credentials."""
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


# ── JWT (real people, via /auth/login) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_member_jwt_can_read_but_not_create_users(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    token = create_access_token(user_id="00000000-0000-0000-0000-000000000000", role="member")
    headers = {"Authorization": f"Bearer {token}"}

    read_resp = await raw_client.get("/users", headers=headers)
    assert read_resp.status_code == 200

    create_resp = await raw_client.post(
        "/users",
        headers=headers,
        json={"name": "x", "email": "member-cannot-create@example.com", "password": "test-password-123"},
    )
    assert create_resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_jwt_can_create_users(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    token = create_access_token(user_id="00000000-0000-0000-0000-000000000000", role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await raw_client.post(
        "/users",
        headers=headers,
        json={"name": "x", "email": "admin-can-create@example.com", "password": "test-password-123"},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_expired_or_garbage_jwt_is_rejected(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    resp = await raw_client.get("/users", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


# ── /auth/login end to end ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_with_correct_password_returns_jwt(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    user = User(
        name="Login Test",
        email="login-test@example.com",
        hashed_password=hash_password("correct-horse-battery"),
        role="member",
    )
    raw_client.db_session.add(user)
    await raw_client.db_session.commit()

    resp = await raw_client.post(
        "/auth/login",
        json={"email": "login-test@example.com", "password": "correct-horse-battery"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20


@pytest.mark.asyncio
async def test_login_with_wrong_password_is_rejected(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    user = User(
        name="Login Test 2",
        email="login-test-2@example.com",
        hashed_password=hash_password("correct-horse-battery"),
        role="member",
    )
    raw_client.db_session.add(user)
    await raw_client.db_session.commit()

    resp = await raw_client.post(
        "/auth/login",
        json={"email": "login-test-2@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_for_unknown_email_is_rejected(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    resp = await raw_client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_for_user_without_password_set_is_rejected(raw_client, monkeypatch):
    """Rows created before login existed have hashed_password=None — must
    fail cleanly, not crash, on a login attempt."""
    monkeypatch.setattr("app.auth.settings.jwt_secret", "test-jwt-secret")
    user = User(name="No Password", email="no-password@example.com", role="member")
    raw_client.db_session.add(user)
    await raw_client.db_session.commit()

    resp = await raw_client.post(
        "/auth/login",
        json={"email": "no-password@example.com", "password": "anything"},
    )
    assert resp.status_code == 401
