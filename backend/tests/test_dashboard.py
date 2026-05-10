import pytest
from httpx import AsyncClient

from tests.test_applications import create_application


@pytest.mark.asyncio
async def test_dashboard_summary_counts_resources_and_applications_by_status(client: AsyncClient):
    first = await create_application(client)
    second = await create_application(client)
    await client.patch(f"/applications/{first['id']}", json={"status": "contacted"})
    await client.patch(f"/applications/{second['id']}", json={"status": "interviewing"})

    response = await client.get("/dashboard/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_companies"] == 2
    assert summary["total_users"] == 2
    assert summary["total_applications"] == 2
    assert summary["applications_by_status"]["contacted"] == 1
    assert summary["applications_by_status"]["interviewing"] == 1

