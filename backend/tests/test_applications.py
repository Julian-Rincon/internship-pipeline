from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_company(client: AsyncClient) -> str:
    response = await client.post(
        "/companies",
        json={"name": "Application Test Company", "domain": f"application-company-{uuid4().hex}.test"},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_user(client: AsyncClient) -> str:
    response = await client.post(
        "/users",
        json={
            "name": "Application Test User",
            "email": f"application-user-{uuid4().hex}@example.com",
            "role": "member",
            "profile_status": "incomplete",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_contact(client: AsyncClient, company_id: str) -> str:
    response = await client.post(
        "/contacts",
        json={"company_id": company_id, "full_name": "Application Test Contact", "source": "manual"},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_application(client: AsyncClient, *, with_contact: bool = False) -> dict:
    company_id = await create_company(client)
    user_id = await create_user(client)
    contact_id = await create_contact(client, company_id) if with_contact else None
    payload = {
        "company_id": company_id,
        "user_id": user_id,
        "contact_id": contact_id,
        "type": "formal",
        "status": "researching",
        "next_action": "Review fictional company page.",
        "next_action_due": "2027-01-15",
        "notes": "Manual test application.",
    }
    response = await client.post("/applications", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_application_with_company_and_user(client: AsyncClient):
    application = await create_application(client)

    assert application["type"] == "formal"
    assert application["status"] == "researching"
    assert application["contact_id"] is None


@pytest.mark.asyncio
async def test_create_application_with_optional_contact(client: AsyncClient):
    application = await create_application(client, with_contact=True)

    assert application["contact_id"] is not None


@pytest.mark.asyncio
async def test_list_applications(client: AsyncClient):
    application = await create_application(client)

    response = await client.get("/applications")

    assert response.status_code == 200
    assert any(item["id"] == application["id"] for item in response.json())


@pytest.mark.asyncio
async def test_get_application_by_id(client: AsyncClient):
    application = await create_application(client)

    response = await client.get(f"/applications/{application['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == application["id"]


@pytest.mark.asyncio
async def test_update_application_status(client: AsyncClient):
    application = await create_application(client)

    response = await client.patch(f"/applications/{application['id']}", json={"status": "contacted"})

    assert response.status_code == 200
    assert response.json()["status"] == "contacted"


@pytest.mark.asyncio
async def test_update_next_action_and_due_date(client: AsyncClient):
    application = await create_application(client)

    response = await client.patch(
        f"/applications/{application['id']}",
        json={"next_action": "Prepare manual follow-up note.", "next_action_due": "2027-02-01"},
    )

    assert response.status_code == 200
    assert response.json()["next_action"] == "Prepare manual follow-up note."
    assert response.json()["next_action_due"] == "2027-02-01"


@pytest.mark.asyncio
async def test_update_application_notes(client: AsyncClient):
    application = await create_application(client)

    response = await client.patch(
        f"/applications/{application['id']}",
        json={"notes": "Updated manual notes."},
    )

    assert response.status_code == 200
    assert response.json()["notes"] == "Updated manual notes."


@pytest.mark.asyncio
async def test_delete_application(client: AsyncClient):
    application = await create_application(client)

    delete_response = await client.delete(f"/applications/{application['id']}")
    missing_response = await client.get(f"/applications/{application['id']}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_create_application_rejects_missing_company(client: AsyncClient):
    user_id = await create_user(client)

    response = await client.post(
        "/applications",
        json={
            "company_id": str(uuid4()),
            "user_id": user_id,
            "type": "formal",
            "status": "researching",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_create_application_rejects_missing_user(client: AsyncClient):
    company_id = await create_company(client)

    response = await client.post(
        "/applications",
        json={
            "company_id": company_id,
            "user_id": str(uuid4()),
            "type": "formal",
            "status": "researching",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_create_application_rejects_missing_contact(client: AsyncClient):
    company_id = await create_company(client)
    user_id = await create_user(client)

    response = await client.post(
        "/applications",
        json={
            "company_id": company_id,
            "user_id": user_id,
            "contact_id": str(uuid4()),
            "type": "formal",
            "status": "researching",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_create_application_rejects_contact_from_other_company(client: AsyncClient):
    company_id = await create_company(client)
    other_company_id = await create_company(client)
    user_id = await create_user(client)
    other_contact_id = await create_contact(client, other_company_id)

    response = await client.post(
        "/applications",
        json={
            "company_id": company_id,
            "user_id": user_id,
            "contact_id": other_contact_id,
            "type": "formal",
            "status": "researching",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Contact does not belong to application company."
