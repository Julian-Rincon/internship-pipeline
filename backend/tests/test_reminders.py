from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.models.company import Company
from tests.test_applications import create_application
from tests.test_companies import create_test_company, create_test_user


async def create_application_with_due_date(
    client: AsyncClient,
    due_date,
    *,
    status: str = "researching",
) -> dict:
    application = await create_application(client)
    response = await client.patch(
        f"/applications/{application['id']}",
        json={
            "status": status,
            "next_action": "Complete manual reminder test action.",
            "next_action_due": due_date.isoformat(),
        },
    )
    assert response.status_code == 200
    return response.json()


def reminders_of_type(reminders: list[dict], reminder_type: str) -> list[dict]:
    return [reminder for reminder in reminders if reminder["type"] == reminder_type]


@pytest.mark.asyncio
async def test_overdue_application_reminder(client: AsyncClient):
    due_date = datetime.now(UTC).date() - timedelta(days=1)
    application = await create_application_with_due_date(client, due_date)

    response = await client.get("/reminders")

    assert response.status_code == 200
    overdue = reminders_of_type(response.json(), "application_overdue")
    assert any(reminder["related_entity_id"] == application["id"] for reminder in overdue)
    assert any(reminder["severity"] == "high" for reminder in overdue)


@pytest.mark.asyncio
async def test_due_today_application_reminder(client: AsyncClient):
    due_date = datetime.now(UTC).date()
    application = await create_application_with_due_date(client, due_date)

    response = await client.get("/reminders")

    assert response.status_code == 200
    due_today = reminders_of_type(response.json(), "application_due_today")
    assert any(reminder["related_entity_id"] == application["id"] for reminder in due_today)


@pytest.mark.asyncio
async def test_due_soon_application_reminder(client: AsyncClient):
    due_date = datetime.now(UTC).date() + timedelta(days=3)
    application = await create_application_with_due_date(client, due_date)

    response = await client.get("/reminders?days_ahead=7")

    assert response.status_code == 200
    due_soon = reminders_of_type(response.json(), "application_due_soon")
    assert any(reminder["related_entity_id"] == application["id"] for reminder in due_soon)


@pytest.mark.asyncio
async def test_ignored_application_statuses_do_not_create_overdue_reminders(client: AsyncClient):
    due_date = datetime.now(UTC).date() - timedelta(days=1)
    applications = [
        await create_application_with_due_date(client, due_date, status=status)
        for status in ["offer", "rejected", "paused"]
    ]

    response = await client.get("/reminders")

    assert response.status_code == 200
    overdue_ids = {
        reminder["related_entity_id"]
        for reminder in reminders_of_type(response.json(), "application_overdue")
    }
    assert all(application["id"] not in overdue_ids for application in applications)


@pytest.mark.asyncio
async def test_pending_discovery_candidate_reminder(client: AsyncClient):
    discovery_response = await client.post("/discovery-candidates/run-demo-discovery")
    assert discovery_response.status_code == 200
    candidate = discovery_response.json()["candidates"][0]
    if candidate["status"] != "pending_review":
        patch_response = await client.patch(
            f"/discovery-candidates/{candidate['id']}",
            json={"status": "pending_review"},
        )
        assert patch_response.status_code == 200
        candidate = patch_response.json()

    response = await client.get("/reminders")

    assert response.status_code == 200
    pending = reminders_of_type(response.json(), "discovery_pending_review")
    assert any(reminder["related_entity_id"] == candidate["id"] for reminder in pending)


@pytest.mark.asyncio
async def test_stale_claimed_company_reminder(client: AsyncClient):
    company = await create_test_company(client)
    user = await create_test_user(client)
    claim_response = await client.post(
        f"/companies/{company['id']}/claim",
        json={"user_id": user["id"]},
    )
    assert claim_response.status_code == 200

    old_claimed_at = datetime.now(UTC) - timedelta(days=15)
    await client.db_session.execute(
        update(Company)
        .where(Company.id == company["id"])
        .values(claimed_at=old_claimed_at)
    )
    await client.db_session.commit()

    response = await client.get("/reminders")

    assert response.status_code == 200
    stale = reminders_of_type(response.json(), "claimed_company_stale")
    assert any(reminder["related_entity_id"] == company["id"] for reminder in stale)


@pytest.mark.asyncio
async def test_days_ahead_filter(client: AsyncClient):
    due_date = datetime.now(UTC).date() + timedelta(days=5)
    application = await create_application_with_due_date(client, due_date)

    response = await client.get("/reminders?days_ahead=3")

    assert response.status_code == 200
    due_soon_ids = {
        reminder["related_entity_id"]
        for reminder in reminders_of_type(response.json(), "application_due_soon")
    }
    assert application["id"] not in due_soon_ids


@pytest.mark.asyncio
async def test_user_filter_limits_application_and_company_reminders(client: AsyncClient):
    due_date = datetime.now(UTC).date() - timedelta(days=1)
    application = await create_application_with_due_date(client, due_date)
    other_user = await create_test_user(client)

    response = await client.get(f"/reminders?user_id={other_user['id']}")

    assert response.status_code == 200
    application_ids = {
        reminder["related_entity_id"]
        for reminder in response.json()
        if reminder["related_entity_type"] == "application"
    }
    assert application["id"] not in application_ids


@pytest.mark.asyncio
async def test_dashboard_summary_includes_reminder_counts(client: AsyncClient):
    due_date = datetime.now(UTC).date() - timedelta(days=1)
    await create_application_with_due_date(client, due_date)

    response = await client.get("/dashboard/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["overdue_reminders"] >= 1
    assert "due_today_reminders" in summary
    assert "due_soon_reminders" in summary
    assert "pending_review_reminders" in summary
