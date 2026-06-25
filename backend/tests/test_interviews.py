from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_company(client: AsyncClient) -> str:
    response = await client.post(
        "/companies",
        json={"name": "Interview Test Company", "domain": f"interview-company-{uuid4().hex}.test"},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_user(client: AsyncClient) -> str:
    response = await client.post(
        "/users",
        json={
            "name": "Interview Test User",
            "email": f"interview-user-{uuid4().hex}@example.com",
            "role": "member",
            "profile_status": "incomplete",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def create_interview(client: AsyncClient) -> dict:
    company_id = await create_company(client)
    user_id = await create_user(client)
    payload = {
        "company_id": company_id,
        "user_id": user_id,
        "interview_type": "technical",
        "outcome": "pending",
        "notes": "Manual test interview.",
    }
    response = await client.post("/interviews", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_interview(client: AsyncClient):
    interview = await create_interview(client)

    assert interview["interview_type"] == "technical"
    assert interview["outcome"] == "pending"
    assert interview["notes"] == "Manual test interview."


@pytest.mark.asyncio
async def test_list_interviews_empty(client: AsyncClient):
    response = await client.get("/interviews")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_interviews_filtered_by_company(client: AsyncClient):
    interview = await create_interview(client)
    company_id = interview["company_id"]

    response = await client.get(f"/interviews?company_id={company_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(item["company_id"] == company_id for item in data)


@pytest.mark.asyncio
async def test_get_interview_not_found(client: AsyncClient):
    response = await client.get(f"/interviews/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_interview_outcome(client: AsyncClient):
    interview = await create_interview(client)

    response = await client.patch(f"/interviews/{interview['id']}", json={"outcome": "passed"})

    assert response.status_code == 200
    assert response.json()["outcome"] == "passed"


@pytest.mark.asyncio
async def test_delete_interview(client: AsyncClient):
    interview = await create_interview(client)

    delete_response = await client.delete(f"/interviews/{interview['id']}")
    missing_response = await client.get(f"/interviews/{interview['id']}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404
