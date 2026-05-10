from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.test_applications import create_application


@pytest.mark.asyncio
async def test_dashboard_summary_counts_resources_and_applications_by_status(client: AsyncClient):
    baseline_response = await client.get("/dashboard/summary")
    assert baseline_response.status_code == 200
    baseline = baseline_response.json()

    first = await create_application(client)
    second = await create_application(client)
    await client.patch(f"/applications/{first['id']}", json={"status": "contacted"})
    await client.patch(f"/applications/{second['id']}", json={"status": "interviewing"})

    response = await client.get("/dashboard/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_companies"] == baseline["total_companies"] + 2
    assert summary["total_users"] == baseline["total_users"] + 2
    assert summary["total_applications"] == baseline["total_applications"] + 2
    assert (
        summary["applications_by_status"]["contacted"]
        == baseline["applications_by_status"].get("contacted", 0) + 1
    )
    assert (
        summary["applications_by_status"]["interviewing"]
        == baseline["applications_by_status"].get("interviewing", 0) + 1
    )


@pytest.mark.asyncio
async def test_dashboard_summary_includes_ownership_counts(client: AsyncClient):
    baseline_response = await client.get("/dashboard/summary")
    assert baseline_response.status_code == 200
    baseline = baseline_response.json()

    company_response = await client.post(
        "/companies",
        json={"name": "Dashboard Ownership Company", "domain": f"dashboard-ownership-{uuid4().hex}.test"},
    )
    user_response = await client.post(
        "/users",
        json={
            "name": "Dashboard Ownership User",
            "email": f"dashboard-ownership-user-{uuid4().hex}@example.com",
            "role": "member",
            "profile_status": "incomplete",
        },
    )
    assert company_response.status_code == 201
    assert user_response.status_code == 201

    claim_response = await client.post(
        f"/companies/{company_response.json()['id']}/claim",
        json={"user_id": user_response.json()["id"]},
    )
    assert claim_response.status_code == 200

    response = await client.get("/dashboard/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["claimed_companies"] == baseline["claimed_companies"] + 1
    assert "unclaimed_companies" in summary
    assert "paused_companies" in summary
    assert "done_companies" in summary
