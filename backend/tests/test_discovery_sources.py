from uuid import uuid4

import pytest
from httpx import AsyncClient


async def create_discovery_source(
    client: AsyncClient,
    *,
    source_type: str = "greenhouse",
    source_key: str | None = None,
    enabled: bool = True,
) -> dict:
    key = source_key or f"source-{uuid4().hex}"
    response = await client.post(
        "/discovery-sources",
        json={
            "name": "ATS Test Source",
            "source_type": source_type,
            "source_key": key,
            "company_hint": "ATS Demo Company",
            "country": "Exampleland",
            "region": "Remote",
            "enabled": enabled,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_discovery_source(client: AsyncClient):
    source = await create_discovery_source(client, source_type="lever")

    assert source["source_type"] == "lever"
    assert source["enabled"] is True


@pytest.mark.asyncio
async def test_reject_duplicate_discovery_source(client: AsyncClient):
    key = f"duplicate-{uuid4().hex}"
    await create_discovery_source(client, source_type="ashby", source_key=key)

    response = await client.post(
        "/discovery-sources",
        json={"name": "Duplicate", "source_type": "ashby", "source_key": key},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_discovery_source(client: AsyncClient):
    source = await create_discovery_source(client)

    response = await client.patch(
        f"/discovery-sources/{source['id']}",
        json={"enabled": False, "company_hint": "Updated Company"},
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["company_hint"] == "Updated Company"


@pytest.mark.asyncio
async def test_delete_discovery_source(client: AsyncClient):
    source = await create_discovery_source(client)

    delete_response = await client.delete(f"/discovery-sources/{source['id']}")
    get_response = await client.get(f"/discovery-sources/{source['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_run_disabled_source_returns_clear_error(client: AsyncClient):
    source = await create_discovery_source(client, enabled=False)

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 400
    assert response.json()["detail"] == "Discovery source is disabled."


@pytest.mark.asyncio
async def test_mocked_greenhouse_fetch_creates_pending_candidates(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return {
            "jobs": [
                {
                    "title": "Software Engineering Intern",
                    "absolute_url": "https://boards.greenhouse.io/demo/jobs/1",
                    "location": {"name": "Remote"},
                    "content": "Internship role",
                }
            ]
        }

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="greenhouse")

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 200
    body = response.json()
    assert body["fetched_count"] == 1
    assert body["internship_like_count"] == 1
    assert body["candidates_created"] == 1

    candidates = await client.get("/discovery-candidates")
    assert any(
        candidate["detected_job_url"] == "https://boards.greenhouse.io/demo/jobs/1"
        and candidate["status"] == "pending_review"
        for candidate in candidates.json()
    )


@pytest.mark.asyncio
async def test_mocked_lever_fetch_creates_pending_candidates(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return [
            {
                "text": "New Grad Backend Engineer",
                "hostedUrl": "https://jobs.lever.co/demo/2",
                "categories": {"location": "Toronto", "commitment": "Full-time"},
                "descriptionPlain": "Early career role",
            }
        ]

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="lever")

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 200
    assert response.json()["candidates_created"] == 1
    candidates = await client.get("/discovery-candidates")
    assert any(candidate["detected_job_url"] == "https://jobs.lever.co/demo/2" for candidate in candidates.json())


@pytest.mark.asyncio
async def test_mocked_ashby_fetch_creates_pending_candidates(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return {
            "jobs": [
                {
                    "title": "Data Science Internship",
                    "jobUrl": "https://jobs.ashbyhq.com/demo/3",
                    "location": "Berlin",
                    "isRemote": False,
                    "descriptionHtml": "Student role",
                }
            ]
        }

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="ashby")

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 200
    assert response.json()["candidates_created"] == 1
    candidates = await client.get("/discovery-candidates")
    assert any(candidate["detected_job_url"] == "https://jobs.ashbyhq.com/demo/3" for candidate in candidates.json())


@pytest.mark.asyncio
async def test_non_internship_jobs_are_filtered_out(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return [
            {
                "text": "Senior Staff Engineer",
                "hostedUrl": "https://jobs.lever.co/demo/senior",
                "categories": {"location": "Remote"},
            }
        ]

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="lever")

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 200
    assert response.json()["fetched_count"] == 1
    assert response.json()["internship_like_count"] == 0
    assert response.json()["candidates_created"] == 0


@pytest.mark.asyncio
async def test_duplicate_job_url_does_not_duplicate_job_posting(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return [
            {
                "text": "Junior Frontend Engineer",
                "hostedUrl": "https://jobs.lever.co/demo/duplicate",
                "categories": {"location": "Remote"},
            }
        ]

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="lever")

    first = await client.post(f"/discovery-sources/{source['id']}/run")
    second = await client.post(f"/discovery-sources/{source['id']}/run")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["job_postings_created"] == 1
    assert second.json()["job_postings_created"] == 0
    assert second.json()["candidates_skipped"] == 1

    postings = await client.get("/job-postings")
    matching = [job for job in postings.json() if job["url"] == "https://jobs.lever.co/demo/duplicate"]
    assert len(matching) == 1


@pytest.mark.asyncio
async def test_fetched_candidates_remain_pending_review(client: AsyncClient, monkeypatch):
    async def fake_fetch_json(url: str):
        return [
            {
                "text": "Entry Level Product Engineer",
                "hostedUrl": "https://jobs.lever.co/demo/pending",
                "categories": {"location": "Remote"},
            }
        ]

    monkeypatch.setattr("app.services.ats_sources.fetch_json", fake_fetch_json)
    source = await create_discovery_source(client, source_type="lever")

    response = await client.post(f"/discovery-sources/{source['id']}/run")

    assert response.status_code == 200
    candidates = await client.get("/discovery-candidates")
    candidate = next(
        candidate
        for candidate in candidates.json()
        if candidate["detected_job_url"] == "https://jobs.lever.co/demo/pending"
    )
    assert candidate["status"] == "pending_review"


@pytest.mark.asyncio
async def test_create_getonboard_discovery_source(client: AsyncClient):
    response = await client.post(
        "/discovery-sources",
        json={
            "name": "GetOnBoard Global",
            "source_type": "getonboard",
            "source_key": "global",
            "enabled": True,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "getonboard"
    assert body["source_key"] == "global"


@pytest.mark.asyncio
async def test_getonboard_runner_creates_pending_candidates(client: AsyncClient, monkeypatch):
    created_urls: list[str] = []

    async def fake_run_getonboard(db):
        from app.models.discovery_candidate import DiscoveryCandidate

        url = "https://www.getonbrd.com/jobs/demo-ai-corp/data-science-internship"
        created_urls.append(url)
        db.add(
            DiscoveryCandidate(
                company_name="Demo AI Corp",
                source="getonboard",
                source_url="https://www.getonbrd.com/api/v0/search/jobs",
                detected_job_title="Data Science Internship",
                detected_job_url=url,
                confidence_score=0.65,
                status="pending_review",
            )
        )
        await db.commit()
        return 1

    monkeypatch.setattr("app.discovery.runners.getonboard_runner.run_getonboard_discovery", fake_run_getonboard)

    source_resp = await client.post(
        "/discovery-sources",
        json={
            "name": "GetOnBoard Global",
            "source_type": "getonboard",
            "source_key": "global",
            "enabled": True,
        },
    )
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    run_resp = await client.post(f"/discovery-sources/{source_id}/run")
    assert run_resp.status_code == 200
    assert run_resp.json()["candidates_created"] == 1

    candidates_resp = await client.get("/discovery-candidates")
    assert any(
        c["detected_job_url"] == created_urls[0] and c["status"] == "pending_review"
        for c in candidates_resp.json()
    )


@pytest.mark.asyncio
async def test_getonboard_runner_skips_duplicate_url(client: AsyncClient, monkeypatch):
    call_count = 0

    async def fake_run_getonboard(db):
        nonlocal call_count
        call_count += 1
        from sqlalchemy import select

        from app.models.discovery_candidate import DiscoveryCandidate

        url = "https://www.getonbrd.com/jobs/demo-ml-corp/ml-internship"
        existing = await db.scalar(
            select(DiscoveryCandidate).where(DiscoveryCandidate.detected_job_url == url)
        )
        if existing is not None:
            return 0
        db.add(
            DiscoveryCandidate(
                company_name="Demo ML Corp",
                source="getonboard",
                source_url="https://www.getonbrd.com/api/v0/search/jobs",
                detected_job_title="ML Engineering Internship",
                detected_job_url=url,
                confidence_score=0.65,
                status="pending_review",
            )
        )
        await db.commit()
        return 1

    monkeypatch.setattr("app.discovery.runners.getonboard_runner.run_getonboard_discovery", fake_run_getonboard)

    source_resp = await client.post(
        "/discovery-sources",
        json={
            "name": "GetOnBoard Dedup Test",
            "source_type": "getonboard",
            "source_key": "global-dedup",
            "enabled": True,
        },
    )
    source_id = source_resp.json()["id"]

    first = await client.post(f"/discovery-sources/{source_id}/run")
    second = await client.post(f"/discovery-sources/{source_id}/run")

    assert first.json()["candidates_created"] == 1
    assert second.json()["candidates_created"] == 0
    assert call_count == 2
