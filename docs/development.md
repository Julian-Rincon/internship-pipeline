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
