# Internship Pipeline System

Self-hosted platform for organizing an international internship pipeline with companies, team members, contacts, applications and a dashboard.

## Project Status

MVP manual in development.

The current system is intentionally safe and reviewable: it does not scrape websites, send emails, automate outreach, use real personal data, or call external enrichment/LLM APIs. It provides the manual operating layer first, before any future automation.

## Problem

Student teams often apply to internships in a fragmented way:

- company research lives in spreadsheets or chats
- team members duplicate effort without visibility
- contacts and next actions are easy to lose
- application statuses are hard to compare
- automation is risky without a clean source of truth

## Solution

Internship Pipeline System centralizes the manual workflow before automation:

- target companies
- progressive team profiles
- manual contacts
- applications linked to companies, users and contacts
- status board and list views
- dashboard summary for pipeline visibility

This creates a structured base for future discovery, reminders, matching and assisted outreach while keeping human review in the loop.

## Current Features

- Companies CRUD
- Users CRUD with progressive profiles
- Manual contacts CRUD
- Applications tracker
- Applications list and board views by status
- Manual editing of application status, next action, due date and notes
- Controlled application deletion with confirmation
- Filters by status, user, company and type
- Dashboard summary
- Backend tests with pytest
- Alembic migrations
- Docker Compose local environment
- n8n container available as a future complementary orchestrator

## Tech Stack

- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Redis
- Next.js
- Docker Compose
- n8n
- Pytest

## Architecture

```text
Browser
  |
  v
Next.js Frontend
  |
  v
FastAPI Backend
  |
  +--> PostgreSQL
  |
  +--> Redis

n8n runs in Docker Compose as a future complementary orchestrator
for schedules, notifications and webhooks. Core product logic stays
in FastAPI, PostgreSQL and the frontend.
```

## Screenshots

Screenshots below show the current manual MVP. Local screenshot assets are stored under `docs/assets/screenshots/`.

### Dashboard

<img width="1280" height="976" alt="image" src="https://github.com/user-attachments/assets/debb56d7-d5b0-4cc2-9970-47afc1be91e8" />

### Companies

<img width="1280" height="976" alt="image" src="https://github.com/user-attachments/assets/eca816ee-a1ce-4283-a3c3-6afcedfa4cd1" />

### Users

<img width="1280" height="976" alt="image" src="https://github.com/user-attachments/assets/2539802f-f9d3-4832-b91b-68fbe1a35d89" />

### Contacts

<img width="1280" height="976" alt="image" src="https://github.com/user-attachments/assets/87e28cfd-d0cc-4b6f-9e9d-876b157ab2ac" />

### Applications Board

<img width="1280" height="976" alt="image" src="https://github.com/user-attachments/assets/1c4d5d7e-49d8-400f-953a-30fc5b74be6d" />

## Local Setup on Windows PowerShell

Prerequisites:

- Docker Desktop
- Docker Compose v2

Commands:

```powershell
Copy-Item .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend pytest
docker compose run --rm --no-deps frontend npm run validate:build
```

## Demo Data

The repository includes a local demo seed script with fictional data only. It creates sample companies, users, contacts and applications using clearly fake `demo.example` domains. The records are intended for local demos and screenshots, not for production use.

Load demo data after applying migrations:

```powershell
docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_demo_data.py"
```

Local URLs:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- n8n: http://localhost:5678

## API Overview

- `GET /health`
- `/companies`
- `/users`
- `/contacts`
- `/applications`
- `GET /dashboard/summary`

Each resource supports the current MVP CRUD workflow through the FastAPI backend. Detailed schemas are available in Swagger at http://localhost:8000/docs after the stack is running.

## Testing

Run backend tests:

```powershell
docker compose exec backend pytest
```

The test suite overrides the FastAPI database dependency and wraps each test in a transaction with rollback. Tests should not leave companies, users, contacts or applications visible in the development dashboard.

Run frontend build:

```powershell
docker compose run --rm --no-deps frontend npm run validate:build
```

If the dev server ever shows stale `.next` chunk errors after build validation, restart it with a clean Next.js cache:

```powershell
docker compose stop frontend
docker compose run --rm --no-deps frontend npm run clean
docker compose up -d frontend
```

## Safety, Ethics and Compliance

The MVP currently:

- does not scrape LinkedIn or company websites
- does not send emails
- does not automate outreach
- does not use real personal data
- does not call Apollo, Hunter, Resend, OpenAI, Anthropic or similar APIs
- does not publish n8n workflows

The project is designed to build a safe source of truth first. Any future automation should require explicit review, compliance checks and human approval.

## Roadmap

### Phase 1

- improve tracker UX
- add detail views by company and user
- add manual CSV/JSON import

### Phase 2

- internal n8n workflows
- notifications for next actions
- manual reminders

### Phase 3

- assisted technical matching
- controlled enrichment
- LLM draft generation with human review

### Phase 4

- automated discovery
- People Finder
- compliance review and human approval gates

## Portfolio Angle

This project demonstrates:

- full-stack architecture
- backend API design with FastAPI
- relational data modeling with PostgreSQL
- SQLAlchemy 2.0 ORM usage
- Alembic migrations
- Dockerized local development
- backend test isolation
- frontend dashboard development with Next.js
- product thinking around data workflows and automation safety

## Repository Notes

Use `.env.example` as the template for local configuration. Do not commit `.env`, real credentials, API keys, tokens or private data.
