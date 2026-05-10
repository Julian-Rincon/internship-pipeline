from uuid import uuid4

import pytest
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_create_user_with_minimum_fields(client: AsyncClient):
    payload = {
        "name": "Example Member",
        "email": f"member-{uuid4().hex}@example.com",
        "role": "member",
        "profile_status": "incomplete",
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    created = response.json()
    assert created["name"] == payload["name"]
    assert created["email"] == payload["email"]
    assert created["role"] == "member"
    assert created["profile_status"] == "incomplete"
    assert created["github_handle"] is None
    assert created["profile_completed_at"] is None


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    email = f"list-user-{uuid4().hex}@example.com"
    create_response = await client.post(
        "/users",
        json={"name": "List User", "email": email, "role": "member", "profile_status": "incomplete"},
    )
    user_id = create_response.json()["id"]

    response = await client.get("/users")

    assert response.status_code == 200
    assert any(user["id"] == user_id for user in response.json())


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    email = f"get-user-{uuid4().hex}@example.com"
    create_response = await client.post(
        "/users",
        json={"name": "Get User", "email": email, "role": "member", "profile_status": "incomplete"},
    )
    user_id = create_response.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_patch_optional_user_profile_fields(client: AsyncClient):
    email = f"patch-user-{uuid4().hex}@example.com"
    create_response = await client.post(
        "/users",
        json={"name": "Patch User", "email": email, "role": "member", "profile_status": "incomplete"},
    )
    user_id = create_response.json()["id"]

    response = await client.patch(
        f"/users/{user_id}",
        json={
            "github_handle": "example-dev",
            "target_roles": ["backend intern", "platform intern"],
            "technical_interests": ["distributed systems", "databases"],
            "strong_skills": ["python", "sql"],
            "internship_goals": "Practice profile data only.",
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["github_handle"] == "example-dev"
    assert updated["target_roles"] == ["backend intern", "platform intern"]
    assert updated["technical_interests"] == ["distributed systems", "databases"]
    assert updated["strong_skills"] == ["python", "sql"]


@pytest.mark.asyncio
async def test_change_profile_status(client: AsyncClient):
    email = f"status-user-{uuid4().hex}@example.com"
    create_response = await client.post(
        "/users",
        json={"name": "Status User", "email": email, "role": "member", "profile_status": "incomplete"},
    )
    user_id = create_response.json()["id"]

    response = await client.patch(f"/users/{user_id}", json={"profile_status": "ready"})

    assert response.status_code == 200
    assert response.json()["profile_status"] == "ready"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    email = f"delete-user-{uuid4().hex}@example.com"
    create_response = await client.post(
        "/users",
        json={"name": "Delete User", "email": email, "role": "member", "profile_status": "incomplete"},
    )
    user_id = create_response.json()["id"]

    delete_response = await client.delete(f"/users/{user_id}")
    missing_response = await client.get(f"/users/{user_id}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_email_is_rejected(client: AsyncClient):
    email = f"duplicate-user-{uuid4().hex}@example.com"
    payload = {
        "name": "Duplicate User",
        "email": email,
        "role": "member",
        "profile_status": "incomplete",
    }

    first_response = await client.post("/users", json=payload)
    second_response = await client.post("/users", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
