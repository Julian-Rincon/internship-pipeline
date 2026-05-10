from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_company(client: AsyncClient) -> str:
    response = await client.post(
        "/companies",
        json={"name": "Contact Test Company", "domain": f"contact-company-{uuid4().hex}.test"},
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_contact_for_existing_company(client: AsyncClient):
    company_id = await create_company(client)

    response = await client.post(
        "/contacts",
        json={
            "company_id": company_id,
            "full_name": "Manual Fictional Contact",
            "role": "Recruiter",
            "source": "manual",
            "affinity_type": "unknown",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["company_id"] == company_id
    assert created["full_name"] == "Manual Fictional Contact"
    assert created["contacted"] is False


@pytest.mark.asyncio
async def test_list_contacts(client: AsyncClient):
    company_id = await create_company(client)
    create_response = await client.post(
        "/contacts",
        json={"company_id": company_id, "full_name": "List Contact", "source": "manual"},
    )
    contact_id = create_response.json()["id"]

    response = await client.get("/contacts")

    assert response.status_code == 200
    assert any(contact["id"] == contact_id for contact in response.json())


@pytest.mark.asyncio
async def test_get_contact_by_id(client: AsyncClient):
    company_id = await create_company(client)
    create_response = await client.post(
        "/contacts",
        json={"company_id": company_id, "full_name": "Get Contact", "source": "manual"},
    )
    contact_id = create_response.json()["id"]

    response = await client.get(f"/contacts/{contact_id}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "Get Contact"


@pytest.mark.asyncio
async def test_patch_contact(client: AsyncClient):
    company_id = await create_company(client)
    create_response = await client.post(
        "/contacts",
        json={"company_id": company_id, "full_name": "Patch Contact", "source": "manual"},
    )
    contact_id = create_response.json()["id"]

    response = await client.patch(
        f"/contacts/{contact_id}",
        json={
            "role": "Engineer",
            "contacted": True,
            "affinity_type": "engineer",
            "metadata": {"note": "fictional test metadata"},
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["role"] == "Engineer"
    assert updated["contacted"] is True
    assert updated["affinity_type"] == "engineer"
    assert updated["metadata"] == {"note": "fictional test metadata"}


@pytest.mark.asyncio
async def test_delete_contact(client: AsyncClient):
    company_id = await create_company(client)
    create_response = await client.post(
        "/contacts",
        json={"company_id": company_id, "full_name": "Delete Contact", "source": "manual"},
    )
    contact_id = create_response.json()["id"]

    delete_response = await client.delete(f"/contacts/{contact_id}")
    missing_response = await client.get(f"/contacts/{contact_id}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_create_contact_rejects_missing_company(client: AsyncClient):
    response = await client.post(
        "/contacts",
        json={
            "company_id": str(uuid4()),
            "full_name": "Missing Company Contact",
            "source": "manual",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Company not found."

