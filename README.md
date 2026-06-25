# Internship Pipeline System

Self-hosted platform for organizing an international internship pipeline with automated discovery, team coordination, application tracking, and n8n-powered notifications.

## Overview

The system gives student teams a structured, auditable pipeline to go from raw discovery to tracked application — without spreadsheets, without lost contacts, without duplicate company research. Every step requires human review before automation moves forward.

Built by and for students hunting international ML/Data Engineering internships. Designed to be hosted on a friend's server in minutes.

## Project Status

**Production-ready MVP.** All 85 backend tests pass. The system runs fully containerized with Docker Compose, including automated ATS discovery from 15+ real company sources (Greenhouse, Lever, Ashby, GetOnBoard), n8n scheduling workflows, and optional Telegram notifications via JARVIS.

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 + asyncpg |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Migrations | Alembic |
| Frontend | Next.js 14 |
| Orchestration | n8n |
| Container | Docker Compose |
| Tests | pytest + httpx (async) |

## Architecture

```
Browser
  │
  ▼
Next.js Frontend  (:3001)
  │
  ▼
FastAPI Backend   (:8000)
  │
  ├── PostgreSQL  (:5432)  — primary data store
  └── Redis       (:6379)  — cache layer

n8n              (:5678)  — scheduling, ATS runners, Telegram digest
  └── calls backend HTTP endpoints only
      └── POST /discovery-sources/run-enabled
      └── GET  /reminders/n8n-summary
      └── GET  /discovery-candidates
```

n8n never writes data directly to Postgres. All mutations go through the FastAPI backend.

## Features

### Companies
- Full CRUD with domain, tier (A/B/C/D), country, region, ATS type, visa-friendly flag
- Manual company claiming per user — prevents duplicate research
- Ownership states: `unclaimed` → `claimed` → `paused` → `done`
- Company detail page with linked contacts and applications

### Users (Progressive Profiles)
- Create with minimal data (`name`, `email`, `role`)
- Optional fields: `github_handle`, `linkedin_url`, `cv_url`, `portfolio_url`
- Profile targeting: `target_roles`, `target_countries`, `target_regions`, `target_company_types`
- Skills inventory: `strong_skills`, `technical_interests`, `learning_goals`, `internship_goals`
- Profile status: `incomplete` → `in_progress` → `ready`
- User detail page with linked applications

### Contacts
- Manual contacts linked to companies
- Fields: `full_name`, `email`, `title`, `linkedin_url`, `source`, `affinity_type`, `affinity_score`
- No scraping, People Finder, or enrichment

### Applications Tracker
- Links a user + company + optional contact
- Types: `formal`, `speculative`, `referral`, `networking`, `other`
- Status flow: `researching` → `contacted` → `responded` → `interviewing` → `offer` / `rejected` / `paused`
- Next action + due date + notes
- Board view (kanban-style by status) and list view
- Filters by status, user, company, type
- Create application directly from a reviewed job posting

### Discovery Pipeline
- **Demo discovery**: creates fictional `DiscoveryCandidate` records (`.demo.example` URLs) for testing without network calls
- **ATS source intake**: public unauthenticated GET per source — Greenhouse, Lever, Ashby, GetOnBoard
- Each source run creates `pending_review` discovery candidates and open job postings
- Human approval required: approving creates or links a company and links the job posting
- Rejecting marks the candidate out of the active pipeline
- Confidence score (0.0–1.0) per candidate based on title pattern matching

### Discovery Sources (26 configured, 15 enabled)
Real ATS sources pre-configured and ready to run:

| Source | Company | Type | Status |
|---|---|---|---|
| Anthropic | Anthropic | Greenhouse | enabled |
| Scale AI | Scale AI | Greenhouse | enabled |
| Vercel | Vercel | Greenhouse | enabled |
| Cloudflare | Cloudflare | Greenhouse | enabled |
| Databricks | Databricks | Greenhouse | enabled |
| Figma | Figma | Greenhouse | enabled |
| Twilio | Twilio | Greenhouse | enabled |
| Stripe | Stripe | Greenhouse | enabled |
| Airtable | Airtable | Ashby | enabled |
| Notion | Notion | Ashby | enabled |
| Linear | Linear | Ashby | enabled |
| Cohere | Cohere | Ashby | enabled |
| Replit | Replit | Ashby | enabled |
| Perplexity AI | Perplexity AI | Ashby | enabled |
| GetOnBoard | Latam/Remote | GetOnBoard | enabled |

### Job Postings
- Created automatically by ATS source runs and demo discovery
- Link to approved company manually if not auto-linked
- Create application directly from a posting (carries title + URL into notes)
- List view with company link, source, URL

### Internal Reminders
Computed on-the-fly — no reminders table. Zero external API calls.

| Reminder type | Trigger |
|---|---|
| `overdue` | Application `next_action_due` in the past, status is active |
| `due_today` | Application due today |
| `due_soon` | Application due in 1–7 days |
| `pending_review` | `DiscoveryCandidate` with `status=pending_review` |
| `stale_claim` | Company claimed > 14 days, status still `claimed` |

Filters supported: `user_id`, `days_ahead`, `severity`.

### n8n Workflows (3 included)

| Workflow | Schedule | Description |
|---|---|---|
| `internal-reminders-demo.json` | Manual only | Fetches and formats reminders summary for internal inspection |
| `daily-discovery-digest.json` | Mon–Fri 9am | Runs all enabled ATS sources, fetches pending candidates, sends Telegram digest |
| `jarvis-julian-personal-alerts.json` | Mon–Fri 8am/12pm/6pm | Personal ML/AI-filtered alerts for Julian via JARVIS Telegram bot |

All workflows call the backend over the Docker network (`http://backend:8000`). No direct DB access from n8n.

### Dashboard
- Counts: companies, users, contacts, applications
- Ownership breakdown: unclaimed / claimed / paused / done
- Reminder badges: overdue, due today, due soon, pending review
- Pipeline status by application status

## Local Setup

### Prerequisites
- Docker Desktop (or Docker Engine + Compose v2)
- Tested on Linux (Fedora) and Windows with WSL2

### Linux/Mac

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Local URLs:
- **Frontend**: http://localhost:3001
- **Backend / Swagger**: http://localhost:8000/docs
- **n8n**: http://localhost:5678

> **Note:** Port 3001 is used because 3000 may be occupied by other services (e.g., AdGuard). Change `FRONTEND_PORT` in `.env` if needed.

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

### Apply Migrations (first run and after updates)

```bash
docker compose exec backend alembic upgrade head
```

### Run Backend Tests

```bash
docker compose exec backend pytest -v
# Expected: 85 passed
```

### Load Demo Data (optional)

```bash
docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_demo_data.py"
docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_discovery_sources.py"
```

## Production / Self-Host

The stack is designed to be dropped onto any Linux server with Docker.

```bash
# On your server
git clone <repo> internship-pipeline
cd internship-pipeline
cp .env.example .env
# Edit .env: set real passwords, FRONTEND_PORT, N8N_HOST, N8N_PROTOCOL
docker compose up -d
docker compose exec backend alembic upgrade head
```

For production:
- Set strong passwords in `.env` (`POSTGRES_PASSWORD`, `N8N_BASIC_AUTH_PASSWORD`, `N8N_ENCRYPTION_KEY`)
- Set `N8N_HOST` to your server domain or IP
- Configure a reverse proxy (nginx/caddy) for HTTPS if exposing externally
- Do not expose PostgreSQL port (5432) publicly

See [deploy-railway.md](docs/deploy-railway.md) for Railway.app deployment.

## n8n Setup

1. Open http://localhost:5678
2. Login: `local-admin` / `change-me-local-only` (change in `.env`)
3. Import workflows from `n8n/workflows/`:
   - Settings → Workflows → Import from file
4. For Telegram notifications:
   - Credentials → New → Telegram API → paste bot token
   - Set `TELEGRAM_CHAT_ID` env var in `.env`
5. Activate the daily digest or JARVIS workflow

### JARVIS Personal Alerts (optional, private)

The `jarvis-julian-personal-alerts.json` workflow sends ML/AI-filtered pipeline alerts to Julian's Telegram via JARVIS bot. It runs 3× per day on weekdays, filtering discovery candidates by ML/AI/Data Engineering keywords and application reminders by user. Configure:

```bash
# In .env (do not commit if sharing the repo)
TELEGRAM_CHAT_ID=<your-chat-id>
JARVIS_TELEGRAM_BOT_TOKEN=<your-bot-token>
```

Then restart n8n: `docker compose restart n8n` and configure the "JARVIS Bot" credential in n8n with the bot token.

## API Reference

All endpoints are documented at http://localhost:8000/docs (Swagger UI).

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET/POST | `/companies` | List / create companies |
| GET/PATCH/DELETE | `/companies/{id}` | Company detail |
| POST | `/companies/{id}/claim` | Claim company |
| POST | `/companies/{id}/release` | Release company |
| PATCH | `/companies/{id}/ownership` | Update ownership status |
| GET/POST | `/users` | List / create users |
| GET/PATCH/DELETE | `/users/{id}` | User detail |
| GET/POST | `/contacts` | List / create contacts |
| GET/PATCH/DELETE | `/contacts/{id}` | Contact detail |
| GET/POST | `/applications` | List / create applications |
| GET/PATCH/DELETE | `/applications/{id}` | Application detail |
| GET | `/discovery-candidates` | List candidates (filter by status) |
| POST | `/discovery-candidates/run-demo-discovery` | Run demo discovery |
| POST | `/discovery-candidates/{id}/approve` | Approve candidate |
| POST | `/discovery-candidates/{id}/reject` | Reject candidate |
| GET/POST | `/discovery-sources` | List / create ATS sources |
| PATCH/DELETE | `/discovery-sources/{id}` | Update / delete source |
| POST | `/discovery-sources/{id}/run` | Run a single source |
| POST | `/discovery-sources/run-enabled` | Run all enabled sources |
| GET | `/job-postings` | List job postings |
| PATCH | `/job-postings/{id}/link-company` | Link posting to company |
| POST | `/job-postings/{id}/create-application` | Create application from posting |
| GET | `/reminders` | List reminders (supports filters) |
| GET | `/reminders/n8n-summary` | Compact summary for n8n |
| GET | `/dashboard/summary` | Dashboard counts |

## Testing

### Unit / Integration Tests

```bash
docker compose exec backend pytest -v
# 85 passed, 0 failed
```

Tests use `AsyncSession` with per-test transaction rollback. No test data leaks to the dashboard.

### Stress Test

The included stress test script (`scripts/` or run via Python) validates:
- 5 workers × 10 iterations: 179 req/s, P99 215ms ✓
- 20 workers × 10 iterations: 514 req/s, P99 239ms ✓
- 50 workers × 5 iterations: 480 req/s, P99 328ms ✓

All scenarios: 0 errors.

```bash
python3 scripts/stress_test.py
```

### Frontend Build Validation

```bash
docker compose run --rm --no-deps frontend npm run validate:build
```

## Safety and Compliance

This system currently:
- Does **not** scrape LinkedIn or company websites
- Only calls **public unauthenticated ATS JSON endpoints**
- Does **not** use Apollo, Hunter, or any People Finder
- Does **not** send emails or automate outreach
- Does **not** use real personal data in demo records
- Does **not** call OpenAI, Anthropic, or any LLM API
- Requires **human approval** before any discovery candidate becomes a company

All data in the demo seed uses clearly fake `demo.example` domains. No real personal data.

## Roadmap

**Phase 2 (next)**
- n8n workflows for internal Slack/Discord notifications
- Manual reminder creation and management
- Auth layer (token or session) for multi-user access control

**Phase 3**
- Assisted matching: score candidates against user profiles
- Controlled LLM draft generation with human review
- Company enrichment from public sources with approval gate

**Phase 4**
- Broader automated discovery (web scraping with allowlist + ToS review)
- People Finder with compliance review
- Full outreach queue with human approval

## Repository Notes

- `.env` is gitignored — never commit real credentials
- `credentials.json` and `token.json` are gitignored
- Use `.env.example` as the configuration template
- Migrations live in `backend/alembic/versions/` — always run `alembic upgrade head` after pulling
- Docker volumes persist data between restarts; use `docker compose down -v` only to reset completely

## Portfolio Angle

This project demonstrates:
- Full-stack architecture with clear separation of concerns
- Async FastAPI with SQLAlchemy 2.0 and asyncpg
- Relational data modeling: companies, users, contacts, applications, discovery, ownership
- Alembic migrations with versioned schema evolution
- Dockerized multi-service local development
- Test isolation with per-test transaction rollback (85 tests)
- n8n workflow integration for scheduling and notifications
- Product thinking: human review gates before automation, progressive profiles, ownership coordination
