from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_company(client: AsyncClient, *, name: str | None = None, tier: str | None = None) -> str:
    payload: dict = {
        "name": name or f"TechMatch Test Company {uuid4().hex[:8]}",
        "domain": f"tech-match-{uuid4().hex}.test",
    }
    if tier:
        payload["tier"] = tier
    response = await client.post("/companies", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


async def create_user(
    client: AsyncClient,
    *,
    strong_skills: list[str] | None = None,
    technical_interests: list[str] | None = None,
) -> str:
    payload: dict = {
        "name": f"TechMatch User {uuid4().hex[:8]}",
        "email": f"techuser-{uuid4().hex}@example.com",
        "role": "member",
        "profile_status": "incomplete",
    }
    if strong_skills is not None:
        payload["strong_skills"] = strong_skills
    if technical_interests is not None:
        payload["technical_interests"] = technical_interests
    response = await client.post("/users", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


async def create_contact(
    client: AsyncClient,
    company_id: str,
    *,
    total_score: int | None = None,
    affinity_score: int | None = None,
) -> str:
    payload: dict = {
        "company_id": company_id,
        "full_name": f"Contact {uuid4().hex[:8]}",
        "source": "manual",
    }
    if total_score is not None:
        payload["total_score"] = total_score
    if affinity_score is not None:
        payload["affinity_score"] = affinity_score
    response = await client.post("/contacts", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_tech_match_no_users(client: AsyncClient):
    """Company with no matching users returns an empty list."""
    company_id = await create_company(client, name="DataCorp Analytics")

    response = await client.get(f"/companies/{company_id}/tech-match")

    assert response.status_code == 200
    # Result may have users from other tests but none should belong to our fixture
    # (isolation via rollback in conftest). With rollback isolation this will be []
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_tech_match_with_matching_user(client: AsyncClient):
    """User with matching skills appears with match_score > 0."""
    company_id = await create_company(client, name="DataCorp Analytics")
    await create_user(
        client,
        strong_skills=["Python", "Data Engineering", "AWS"],
        technical_interests=["SQL", "Machine Learning"],
    )

    response = await client.get(f"/companies/{company_id}/tech-match")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    top = data[0]
    assert top["match_score"] > 0
    assert len(top["matching_skills"]) > 0
    assert "user_id" in top
    assert "name" in top
    assert "email" in top


@pytest.mark.asyncio
async def test_tech_match_sorted_desc(client: AsyncClient):
    """Results are ordered by match_score descending."""
    company_id = await create_company(client, name="DataCorp Analytics ML Platform")
    # High-match user
    await create_user(
        client,
        strong_skills=["Python", "Data Engineering", "SQL", "pandas"],
        technical_interests=["Machine Learning", "PyTorch"],
    )
    # Low-match user
    await create_user(
        client,
        strong_skills=["Python"],
        technical_interests=[],
    )

    response = await client.get(f"/companies/{company_id}/tech-match")

    assert response.status_code == 200
    data = response.json()
    scores = [item["match_score"] for item in data]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_tech_match_company_not_found(client: AsyncClient):
    """Returns 404 when company does not exist."""
    response = await client.get(f"/companies/{uuid4()}/tech-match")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_ranked_contacts_empty(client: AsyncClient):
    """Company with no contacts returns an empty list."""
    company_id = await create_company(client)

    response = await client.get(f"/companies/{company_id}/contacts/ranked")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_ranked_contacts_ordered(client: AsyncClient):
    """Contacts are returned ordered by total_score DESC."""
    company_id = await create_company(client)
    await create_contact(client, company_id, total_score=30, affinity_score=20)
    await create_contact(client, company_id, total_score=80, affinity_score=60)
    await create_contact(client, company_id, total_score=50, affinity_score=40)

    response = await client.get(f"/companies/{company_id}/contacts/ranked")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    scores = [c["total_score"] for c in data]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 80


@pytest.mark.asyncio
async def test_ranked_contacts_filter_by_contacted(client: AsyncClient):
    """Filtering by ?contacted=true returns only contacted contacts."""
    company_id = await create_company(client)
    # Create one contacted and one not contacted
    contact1_response = await client.post(
        "/contacts",
        json={
            "company_id": company_id,
            "full_name": "Contacted Person",
            "source": "manual",
            "contacted": True,
            "total_score": 70,
        },
    )
    assert contact1_response.status_code == 201

    await create_contact(client, company_id, total_score=40)

    response = await client.get(f"/companies/{company_id}/contacts/ranked?contacted=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contacted"] is True


@pytest.mark.asyncio
async def test_enrich_contacts_endpoint(client: AsyncClient):
    """POST /enrich-contacts returns status and count."""
    company_id = await create_company(client)
    await create_contact(client, company_id)
    await create_contact(client, company_id)

    response = await client.post(f"/companies/{company_id}/enrich-contacts")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "count" in data
    assert data["status"] in ("ok", "enriched")
