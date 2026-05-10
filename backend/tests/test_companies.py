from uuid import uuid4

import pytest
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient):
    unique = uuid4().hex
    payload = {
        "name": "Example Systems",
        "domain": f"example-systems-{unique}.test",
        "tier": "B",
        "country": "Exampleland",
        "region": "EU",
        "careers_url": "https://example-systems.test/careers",
        "ats_type": "custom",
        "visa_friendly_intern": "unknown",
        "status": "active",
    }

    create_response = await client.post("/companies", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == payload["name"]
    assert created["tier"] == "B"


@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient):
    unique = uuid4().hex
    create_response = await client.post(
        "/companies",
        json={"name": "List Example", "domain": f"list-example-{unique}.test"},
    )
    company_id = create_response.json()["id"]

    list_response = await client.get("/companies")
    assert list_response.status_code == 200
    assert any(company["id"] == company_id for company in list_response.json())


@pytest.mark.asyncio
async def test_get_company_by_id(client: AsyncClient):
    unique = uuid4().hex
    payload = {"name": "Get Example", "domain": f"get-example-{unique}.test"}
    create_response = await client.post("/companies", json=payload)
    company_id = create_response.json()["id"]

    get_response = await client.get(f"/companies/{company_id}")
    assert get_response.status_code == 200
    assert get_response.json()["domain"] == payload["domain"]


@pytest.mark.asyncio
async def test_patch_company(client: AsyncClient):
    unique = uuid4().hex
    create_response = await client.post(
        "/companies",
        json={"name": "Patch Example", "domain": f"patch-example-{unique}.test", "tier": "B"},
    )
    company_id = create_response.json()["id"]

    patch_response = await client.patch(f"/companies/{company_id}", json={"tier": "A"})
    assert patch_response.status_code == 200
    assert patch_response.json()["tier"] == "A"


@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient):
    unique = uuid4().hex
    create_response = await client.post(
        "/companies",
        json={"name": "Delete Example", "domain": f"delete-example-{unique}.test"},
    )
    company_id = create_response.json()["id"]

    delete_response = await client.delete(f"/companies/{company_id}")
    assert delete_response.status_code == 204

    missing_response = await client.get(f"/companies/{company_id}")
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_tier_is_rejected(client: AsyncClient):
    response = await client.post(
        "/companies",
        json={
            "name": "Invalid Tier Example",
            "domain": f"invalid-tier-{uuid4().hex}.test",
            "tier": "Z",
        },
    )

    assert response.status_code == 422
