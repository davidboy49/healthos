# VPS Deployment Prompt

You are deploying a private Personal Health OS from this repo onto a VPS.

## Read first

1. `DEPLOYMENT_HANDBOOK.md`
2. `README.md`
3. `docs/operations.md`

## Mission

- Deploy the current repo exactly as it exists.
- Do not redesign the app.
- Do not refactor unless deployment is blocked.
- Keep the system private and evidence-first.

## Stack

- `web`: Next.js dashboard
- `api`: FastAPI backend
- `worker`: Celery worker
- `scheduler`: Celery Beat
- `db`: PostgreSQL + TimescaleDB
- `redis`: queue/broker

## Required setup

1. Copy `.env.example` to `.env`.
2. Fill all secrets and Garmin credentials.
3. Start the stack with Docker Compose.
4. Run migrations.
5. Create the first admin user.
6. Verify `/healthz`, `/docs`, and the dashboard.

## Commands

```bash
docker compose up -d --build db redis api worker scheduler web
docker compose exec api alembic upgrade head
docker compose exec api python -m healthos_api.cli create-admin --email you@example.com --password 'change-me-now'
docker compose ps
```

## Acceptance

- The stack is up.
- The API is reachable.
- The dashboard loads.
- The admin user exists.
- Garmin can be connected later without changing the deployment structure.

## Stop if missing

- Docker or Compose
- A valid `SECRET_KEY`
- A valid `TOKEN_ENCRYPTION_KEY`
- Garmin OAuth credentials
- Domain or public IP plan
- Migration/build errors

If something is missing, report the exact blocker and do not guess.
## Current ingestion priority

Use FitnessSyncer + n8n before Garmin official API.

- Put CSV files in `data/imports` on the VPS.
- Call `POST /imports/fitnesssyncer/local` with the filename.
- Read `docs/n8n/fitnesssyncer-import.md`.
- Test with `samples/fitnesssyncer_mock.csv` first.
