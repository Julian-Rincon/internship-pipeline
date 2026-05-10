# Demo Script

Target length: 3-5 minutes.

## Before the Demo

Start the stack and load fictional demo records:

```powershell
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_demo_data.py"
```

All demo records are fictional and use `demo.example` domains.

## 1. Context (30 seconds)

Explain the problem: internship searches become fragmented across spreadsheets, chats and individual notes.

Position the project as a safe manual MVP. It is not a scraping or outreach automation tool.

## 2. Architecture (45 seconds)

Show the Docker Compose stack:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- n8n available for future orchestration

Mention that core product logic lives in FastAPI, PostgreSQL and the frontend. n8n is present only as future complementary orchestration.

## 3. Product Walkthrough (2 minutes)

Open `http://localhost:3000`.

Show:

- Dashboard summary
- Companies list and manual creation form
- Users with progressive profiles
- Contacts created manually with fictional data
- Applications tracker
- List and board views by status
- Filters by status, user, company and type
- Inline status, next action, due date and notes editing
- Delete confirmation for applications

## 4. API and Engineering (1 minute)

Open Swagger at `http://localhost:8000/docs`.

Mention:

- REST resources
- Alembic migrations
- pytest isolation
- no real credentials or external APIs

Also mention `GET /dashboard/summary` as the dashboard aggregation endpoint.

## 5. Roadmap (30 seconds)

Close with planned phases:

- better manual UX
- internal reminders
- controlled matching/enrichment
- later discovery and People Finder with compliance and human review

End by reiterating that automation would only be added with compliance checks and human review.
