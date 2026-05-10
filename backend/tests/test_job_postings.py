from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models.job_posting import JobPosting
from tests.test_applications import create_company, create_user


async def create_job_posting(client: AsyncClient, *, title: str = "Software Engineering Intern") -> dict:
    job_posting = JobPosting(
        title=title,
        url=f"https://jobs.example.test/{uuid4().hex}",
        location="Remote",
        remote=True,
        description="Fictional test posting.",
        source="test_source",
        status="open",
    )
    client.db_session.add(job_posting)
    await client.db_session.commit()
    await client.db_session.refresh(job_posting)
    return {
        "id": str(job_posting.id),
        "title": job_posting.title,
        "url": job_posting.url,
        "source": job_posting.source,
    }


async def create_linkable_job_posting(client: AsyncClient) -> dict:
    return await create_job_posting(client)


@pytest.mark.asyncio
async def test_list_job_postings_with_filters(client: AsyncClient):
    posting = await create_linkable_job_posting(client)

    by_status = await client.get("/job-postings?status=open")
    by_source = await client.get(f"/job-postings?source={posting['source']}")
    by_title = await client.get(f"/job-postings?title={posting['title'].split()[0]}")

    assert by_status.status_code == 200
    assert by_source.status_code == 200
    assert by_title.status_code == 200
    assert any(job["id"] == posting["id"] for job in by_status.json())
    assert any(job["id"] == posting["id"] for job in by_source.json())
    assert any(job["id"] == posting["id"] for job in by_title.json())


@pytest.mark.asyncio
async def test_link_job_posting_to_company(client: AsyncClient):
    posting = await create_linkable_job_posting(client)
    company_id = await create_company(client)

    response = await client.patch(
        f"/job-postings/{posting['id']}/link-company",
        json={"company_id": company_id},
    )

    assert response.status_code == 200
    assert response.json()["company_id"] == company_id


@pytest.mark.asyncio
async def test_link_job_posting_to_nonexistent_company_returns_error(client: AsyncClient):
    posting = await create_linkable_job_posting(client)

    response = await client.patch(
        f"/job-postings/{posting['id']}/link-company",
        json={"company_id": str(uuid4())},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_create_application_from_linked_job_posting(client: AsyncClient):
    posting = await create_linkable_job_posting(client)
    company_id = await create_company(client)
    user_id = await create_user(client)
    await client.patch(f"/job-postings/{posting['id']}/link-company", json={"company_id": company_id})

    response = await client.post(
        f"/job-postings/{posting['id']}/create-application",
        json={
            "user_id": user_id,
            "next_action": "Review application requirements.",
            "next_action_due": "2027-03-01",
            "notes": "Manual application from reviewed posting.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["company_id"] == company_id
    assert body["user_id"] == user_id
    assert body["type"] == "formal"
    assert body["status"] == "researching"


@pytest.mark.asyncio
async def test_create_application_from_job_posting_without_company_returns_clear_error(client: AsyncClient):
    posting = await create_linkable_job_posting(client)

    response = await client.post(
        f"/job-postings/{posting['id']}/create-application",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Job posting must be linked to an approved company before creating an application."
    )


@pytest.mark.asyncio
async def test_create_application_from_job_posting_with_nonexistent_user_returns_error(client: AsyncClient):
    posting = await create_linkable_job_posting(client)
    company_id = await create_company(client)
    await client.patch(f"/job-postings/{posting['id']}/link-company", json={"company_id": company_id})

    response = await client.post(
        f"/job-postings/{posting['id']}/create-application",
        json={"user_id": str(uuid4())},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_application_notes_include_job_context(client: AsyncClient):
    posting = await create_linkable_job_posting(client)
    company_id = await create_company(client)
    user_id = await create_user(client)
    await client.patch(f"/job-postings/{posting['id']}/link-company", json={"company_id": company_id})

    response = await client.post(
        f"/job-postings/{posting['id']}/create-application",
        json={"user_id": user_id, "notes": "Team reviewed this opportunity."},
    )

    assert response.status_code == 200
    notes = response.json()["notes"]
    assert "Team reviewed this opportunity." in notes
    assert posting["title"] in notes
    assert posting["url"] in notes
