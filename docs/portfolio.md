# Portfolio Notes

## What This Project Demonstrates

Internship Pipeline System is a full-stack MVP for coordinating an international internship search workflow. It shows how to build a structured, self-hosted internal tool before adding risky automation.

## Technical Highlights

- FastAPI API design with typed schemas.
- SQLAlchemy 2.0 models and PostgreSQL relationships.
- Alembic migration history for incremental schema changes.
- Next.js dashboard with list, board, filters and inline edits.
- Docker Compose orchestration for backend, frontend, Postgres, Redis and n8n.
- Pytest coverage with transaction rollback so tests do not pollute visible dev data.

## Product Angle

The product solves a coordination problem: a team needs shared visibility into companies, team members, contacts, applications and next actions. The MVP keeps all data manual so the team can validate workflow quality before adding discovery, matching or outreach automation.

## Safety Angle

The project explicitly avoids scraping, real personal data, automated emails and external enrichment APIs in the MVP. This makes it a good example of building automation-oriented products with review gates and compliance in mind.

