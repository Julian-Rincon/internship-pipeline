# Demo Script

Target length: 3-5 minutes.

## 1. Context

Explain the problem: internship searches become fragmented across spreadsheets, chats and individual notes.

## 2. Architecture

Show the Docker Compose stack:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- n8n available for future orchestration

## 3. Product Walkthrough

Open `http://localhost:3000`.

Show:

- Dashboard summary
- Companies list and creation form
- Users with progressive profiles
- Contacts created manually
- Applications tracker
- List and board views
- Filters
- Inline status/next action editing

## 4. API and Engineering

Open Swagger at `http://localhost:8000/docs`.

Mention:

- REST resources
- Alembic migrations
- pytest isolation
- no real credentials or external APIs

## 5. Roadmap

Close with planned phases:

- better manual UX
- internal reminders
- controlled matching/enrichment
- later discovery and People Finder with compliance and human review

