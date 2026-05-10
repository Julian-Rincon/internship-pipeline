from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_test_company(client: AsyncClient) -> dict:
    response = await client.post(
        "/companies",
        json={"name": "Ownership Test Company", "domain": f"ownership-company-{uuid4().hex}.test"},
    )
    assert response.status_code == 201
    return response.json()


async def create_test_user(client: AsyncClient) -> dict:
    response = await client.post(
        "/users",
        json={
            "name": "Ownership Test User",
            "email": f"ownership-user-{uuid4().hex}@example.com",
            "role": "member",
            "profile_status": "incomplete",
        },
    )
    assert response.status_code == 201
    return response.json()


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


@pytest.mark.asyncio
async def test_claim_unclaimed_company(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)

    response = await client.post(
        f"/companies/{company['id']}/claim",
        json={"user_id": user["id"], "ownership_notes": "Manual owner for outreach coordination."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["owner_user_id"] == user["id"]
    assert body["ownership_status"] == "claimed"
    assert body["claimed_at"] is not None
    assert body["ownership_notes"] == "Manual owner for outreach coordination."


@pytest.mark.asyncio
async def test_claim_with_nonexistent_user_returns_error(client: AsyncClient):
    company = await create_test_company(client)

    response = await client.post(
        f"/companies/{company['id']}/claim",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_claim_already_claimed_by_same_user_is_idempotent(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)

    first = await client.post(f"/companies/{company['id']}/claim", json={"user_id": user["id"]})
    second = await client.post(f"/companies/{company['id']}/claim", json={"user_id": user["id"]})

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["owner_user_id"] == user["id"]
    assert second.json()["ownership_status"] == "claimed"
    assert second.json()["claimed_at"] == first.json()["claimed_at"]


@pytest.mark.asyncio
async def test_claim_already_claimed_by_another_user_returns_409(client: AsyncClient):
    company = await create_test_company(client)
    first_user = await create_test_user(client)
    second_user = await create_test_user(client)

    await client.post(f"/companies/{company['id']}/claim", json={"user_id": first_user["id"]})
    response = await client.post(
        f"/companies/{company['id']}/claim",
        json={"user_id": second_user["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Company is already claimed by another user."


@pytest.mark.asyncio
async def test_release_company(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)
    await client.post(
        f"/companies/{company['id']}/claim",
        json={"user_id": user["id"], "ownership_notes": "Temporary claim."},
    )

    response = await client.post(f"/companies/{company['id']}/release")

    assert response.status_code == 200
    body = response.json()
    assert body["owner_user_id"] is None
    assert body["ownership_status"] == "unclaimed"
    assert body["claimed_at"] is None
    assert body["ownership_notes"] is None


@pytest.mark.asyncio
async def test_update_ownership_status_to_paused(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)
    await client.post(f"/companies/{company['id']}/claim", json={"user_id": user["id"]})

    response = await client.patch(
        f"/companies/{company['id']}/ownership",
        json={"ownership_status": "paused", "ownership_notes": "Waiting for manual review."},
    )

    assert response.status_code == 200
    assert response.json()["ownership_status"] == "paused"
    assert response.json()["ownership_notes"] == "Waiting for manual review."


@pytest.mark.asyncio
async def test_update_ownership_status_to_done(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)
    await client.post(f"/companies/{company['id']}/claim", json={"user_id": user["id"]})

    response = await client.patch(
        f"/companies/{company['id']}/ownership",
        json={"ownership_status": "done"},
    )

    assert response.status_code == 200
    assert response.json()["ownership_status"] == "done"


@pytest.mark.asyncio
async def test_cannot_set_claimed_without_owner(client: AsyncClient):
    company = await create_test_company(client)

    response = await client.patch(
        f"/companies/{company['id']}/ownership",
        json={"ownership_status": "claimed"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Cannot mark company as claimed without an owner."
