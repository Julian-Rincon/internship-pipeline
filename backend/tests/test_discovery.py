import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_demo_discovery_creates_or_reuses_candidates(client: AsyncClient):
    response = await client.post("/discovery-candidates/run-demo-discovery")

    assert response.status_code == 200
    body = response.json()
    assert body["candidates_created"] >= 0
    assert body["job_postings_created"] >= 0
    assert len(body["candidates"]) == 3
    assert all(
        candidate["status"] in {"pending_review", "approved", "rejected", "ignored"}
        for candidate in body["candidates"]
    )
    assert all(candidate["domain"].endswith(".demo.example") for candidate in body["candidates"])


@pytest.mark.asyncio
async def test_list_discovery_candidates(client: AsyncClient):
    await client.post("/discovery-candidates/run-demo-discovery")

    response = await client.get("/discovery-candidates")

    assert response.status_code == 200
    assert len(response.json()) >= 3


@pytest.mark.asyncio
async def test_get_discovery_candidate_by_id(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate_id = create_response.json()["candidates"][0]["id"]

    response = await client.get(f"/discovery-candidates/{candidate_id}")

    assert response.status_code == 200
    assert response.json()["id"] == candidate_id


@pytest.mark.asyncio
async def test_approve_candidate_creates_company(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate = create_response.json()["candidates"][0]

    approve_response = await client.post(f"/discovery-candidates/{candidate['id']}/approve")

    assert approve_response.status_code == 200
    company = approve_response.json()
    assert company["name"] == candidate["company_name"]
    assert company["domain"] == candidate["domain"]

    get_response = await client.get(f"/discovery-candidates/{candidate['id']}")
    assert get_response.json()["status"] == "approved"
    assert get_response.json()["reviewed_at"] is not None


@pytest.mark.asyncio
async def test_approve_duplicate_candidate_does_not_create_duplicate_company(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate = create_response.json()["candidates"][0]

    first_approval = await client.post(f"/discovery-candidates/{candidate['id']}/approve")
    second_approval = await client.post(f"/discovery-candidates/{candidate['id']}/approve")

    assert first_approval.status_code == 200
    assert second_approval.status_code == 200
    assert second_approval.json()["id"] == first_approval.json()["id"]

    companies_response = await client.get("/companies")
    matching_companies = [
        company for company in companies_response.json() if company["domain"] == candidate["domain"]
    ]
    assert len(matching_companies) == 1


@pytest.mark.asyncio
async def test_reject_candidate_changes_status(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate_id = create_response.json()["candidates"][0]["id"]

    response = await client.post(f"/discovery-candidates/{candidate_id}/reject")

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["reviewed_at"] is not None


@pytest.mark.asyncio
async def test_list_job_postings(client: AsyncClient):
    await client.post("/discovery-candidates/run-demo-discovery")

    response = await client.get("/job-postings")

    assert response.status_code == 200
    demo_postings = [jp for jp in response.json() if jp["source"] == "demo_discovery"]
    assert len(demo_postings) >= 3


@pytest.mark.asyncio
async def test_invalid_discovery_candidate_status_is_rejected(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate_id = create_response.json()["candidates"][0]["id"]

    response = await client.patch(
        f"/discovery-candidates/{candidate_id}",
        json={"status": "needs_research"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_cannot_bypass_discovery_approval(client: AsyncClient):
    create_response = await client.post("/discovery-candidates/run-demo-discovery")
    candidate_id = create_response.json()["candidates"][0]["id"]

    response = await client.patch(
        f"/discovery-candidates/{candidate_id}",
        json={"status": "approved"},
    )

    assert response.status_code == 400
    assert "approve or reject endpoint" in response.json()["detail"]
