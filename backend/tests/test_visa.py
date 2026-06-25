from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_company(client: AsyncClient) -> str:
    response = await client.post(
        "/companies",
        json={"name": "Visa Test Company", "domain": f"visa-company-{uuid4().hex}.test"},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_visa_data(client: AsyncClient) -> dict:
    company_id = await create_company(client)
    payload = {
        "company_id": company_id,
        "country": "Germany",
        "intern_friendly": "green",
        "visa_type": "Praktikantenbewilligung",
        "sponsor_verified": True,
        "notes": "Manual test visa entry.",
    }
    response = await client.post("/visa", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_visa_data(client: AsyncClient):
    visa = await create_visa_data(client)

    assert visa["country"] == "Germany"
    assert visa["intern_friendly"] == "green"
    assert visa["visa_type"] == "Praktikantenbewilligung"
    assert visa["sponsor_verified"] is True


@pytest.mark.asyncio
async def test_list_visa_data_empty(client: AsyncClient):
    response = await client.get("/visa")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_visa_by_company(client: AsyncClient):
    visa = await create_visa_data(client)
    company_id = visa["company_id"]

    response = await client.get(f"/visa/by-company/{company_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(item["company_id"] == company_id for item in data)


@pytest.mark.asyncio
async def test_update_visa_intern_friendly(client: AsyncClient):
    visa = await create_visa_data(client)

    response = await client.patch(f"/visa/{visa['id']}", json={"intern_friendly": "yellow"})

    assert response.status_code == 200
    assert response.json()["intern_friendly"] == "yellow"


@pytest.mark.asyncio
async def test_delete_visa_data(client: AsyncClient):
    visa = await create_visa_data(client)

    delete_response = await client.delete(f"/visa/{visa['id']}")
    missing_response = await client.get(f"/visa/{visa['id']}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404
