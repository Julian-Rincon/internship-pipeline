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
docker compose run --rm frontend npm run build
```

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
