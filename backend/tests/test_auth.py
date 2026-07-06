"""Dedicated coverage for verify_api_key — the real dependency, not bypassed.

Every other test file overrides verify_api_key (see conftest.py) to focus on
business logic. This file is the only one that exercises the actual auth
check, using its own client fixture without that override.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def raw_client():
    """Client WITHOUT the verify_api_key override — real auth enforced."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest.mark.asyncio
async def test_health_is_public_without_api_key(raw_client):
    resp = await raw_client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_protected_route_rejects_missing_key(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_rejects_wrong_key(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_accepts_correct_key(raw_client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.get("/users", headers={"X-API-Key": "real-secret"})
    # 200 (or whatever the route returns) — the point is it's NOT 401/503;
    # the DB isn't set up on this client so we only assert auth passed through.
    assert resp.status_code != 401 and resp.status_code != 503


@pytest.mark.asyncio
async def test_unconfigured_api_key_fails_closed(raw_client, monkeypatch):
    """No API_KEY set on the server at all → refuse every protected route,
    never silently allow access. This is the 'someone forgot to configure
    it before deploying' case."""
    monkeypatch.setattr("app.auth.settings.api_key", "")
    resp = await raw_client.get("/users", headers={"X-API-Key": "anything"})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_delete_user_requires_api_key(raw_client, monkeypatch):
    """Regression for the exact finding from the security review: DELETE
    on any user_id must not be reachable without the key."""
    monkeypatch.setattr("app.auth.settings.api_key", "real-secret")
    resp = await raw_client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401
