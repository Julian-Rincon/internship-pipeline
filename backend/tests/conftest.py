import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.db import engine, get_db
from app.main import app


@pytest_asyncio.fixture
async def client():
    """Auth is bypassed here on purpose: these 104+ tests exercise business
    logic (CRUD, reminders, tech matching...), not the auth mechanism itself.
    Overriding require_auth to return None (the "authenticated as a trusted
    service" case) also satisfies require_admin, since it depends on
    require_auth internally — FastAPI's dependency_overrides replaces the
    callable everywhere it's used, not just at the top level.
    See test_auth.py for the dedicated, non-bypassed coverage."""
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = lambda: None

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
            test_client.db_session = session
            yield test_client
    finally:
        await session.close()
        app.dependency_overrides.clear()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
        await engine.dispose()
