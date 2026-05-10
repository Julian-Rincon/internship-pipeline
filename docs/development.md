# Development Guide

## Start Local Stack

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Apply Migrations

```powershell
docker compose exec backend alembic upgrade head
```

## Run Backend Tests

```powershell
docker compose exec backend pytest
```

Tests use a FastAPI dependency override and transaction rollback per test. They should not leave visible test data in the development dashboard.

## Validate Frontend

```powershell
docker compose run --rm --no-deps frontend npm run validate:build
```

`validate:build` removes `.next`, runs `next build`, and removes `.next` again. This keeps the development server from reusing stale production build chunks.

## Clean and Restart Frontend Dev

If a route fails with an error like `Cannot find module '../991.js'`, the Next.js cache is stale. Clean and restart the frontend:

```powershell
docker compose stop frontend
docker compose run --rm --no-deps frontend npm run clean
docker compose up -d frontend
```

The Compose setup mounts `/app/.next` as a Docker named volume instead of writing it into the host `frontend/.next` folder. `.next` is still ignored by Git and should never be committed.

## Load Demo Data

After migrations are applied, load fictional demo records:

```powershell
docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_demo_data.py"
```

The seed script is idempotent for the included demo records and uses only fictional names and `demo.example` domains.

## Discovery Development

Discovery is currently demo-only. Use the `/discovery` page or `POST /discovery-candidates/run-demo-discovery` to create fictional pending candidates and demo job postings. The demo flow does not perform HTTP scraping, call external APIs, use LLMs or create n8n workflows.

Candidates must be reviewed before they affect the official companies list. Approval creates or links a company by domain or normalized company name and links the detected job posting to that company when possible. Rejection only updates the candidate status and review timestamp.

Future ATS discovery should stay behind this pending-review layer, use conservative allowlists and avoid aggressive crawling or anti-bot bypasses.

## Company Claiming Development

Company claiming is a manual coordination feature. Use `/companies/{id}` to select a user, add optional notes and claim a company. Claimed companies can be released, or moved between `claimed`, `paused` and `done`.

There is no authentication or permissions layer yet. The selected owner is a normal existing user chosen from a dropdown, so this should be treated as a team planning field rather than an access-control mechanism.

Release resets the company to `unclaimed` and clears `owner_user_id`, `claimed_at` and `ownership_notes`.

## Useful Logs

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f n8n
```

## Stop Services

```powershell
docker compose down
```

## Troubleshooting

If the frontend cannot reach the backend inside Docker, check:

- `INTERNAL_API_URL=http://backend:8000`
- `NEXT_PUBLIC_API_URL=http://localhost:8000`

If n8n logs mention a missing Python task runner, it is not blocking this MVP because no Python Code nodes or production workflows are used.
