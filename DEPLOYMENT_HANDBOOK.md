# Deployment Handbook

## Goal

Deploy this repository as the first usable version of Personal Health OS on a VPS.

The system is a Docker Compose app with:

- `web` for the dashboard
- `api` for the FastAPI backend
- `worker` for background jobs
- `scheduler` for recurring jobs
- `db` for PostgreSQL + TimescaleDB
- `redis` for queueing

## First Files To Read

1. [README.md](./README.md)
2. [docs/implementation.md](./docs/implementation.md)
3. [docs/operations.md](./docs/operations.md)
4. [docker-compose.yml](./docker-compose.yml)
5. [apps/api/README.md](./apps/api/README.md)
6. [apps/web/README.md](./apps/web/README.md)

## What The Agent Should Understand

- This is a private health platform for one user first.
- The dashboard should be deployed as-is.
- Do not redesign the product while deploying it.
- Garmin integration is the intended source of health data.
- The platform should fail safely if Garmin credentials are missing.
- The backend should use deterministic metrics before AI-generated recommendations.

## Required Environment Variables

Start from `.env.example` and fill the real values:

- `APP_ENV`
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `TOKEN_ENCRYPTION_KEY`
- `GARMIN_CLIENT_ID`
- `GARMIN_CLIENT_SECRET`
- `GARMIN_AUTH_URL`
- `GARMIN_TOKEN_URL`
- `GARMIN_API_BASE_URL`
- `NEXT_PUBLIC_API_BASE_URL`

## Deployment Order

1. Clone the repo on the VPS.
2. Copy `.env.example` to `.env`.
3. Fill in secrets and Garmin credentials.
4. Start the stack with Docker Compose.
5. Run database migrations.
6. Create the first admin user.
7. Verify the API health endpoint and the dashboard.
8. Connect Garmin credentials and test sync.

## Exact Commands

```bash
git clone https://github.com/davidboy49/healthos.git
cd healthos
cp .env.example .env
docker compose up -d --build db redis api worker scheduler web
docker compose exec api alembic upgrade head
docker compose exec api python -m healthos_api.cli create-admin --email you@example.com --password 'change-me-now'
docker compose ps
```

## Verification Targets

- `GET /healthz` returns `ok`
- `GET /docs` is reachable
- Dashboard loads in the browser
- Admin user can log in
- `GET /garmin/status` shows whether Garmin is connected
- `POST /garmin/sync` queues a job successfully

## Stop Conditions

If any of these are missing, the agent should stop and report clearly:

- Garmin OAuth credentials
- A working domain or public IP strategy
- A valid `SECRET_KEY`
- A valid `TOKEN_ENCRYPTION_KEY`
- Docker or Compose not installed on the VPS
- Migration errors
- Container build errors
- Authentication failures to GitHub or Garmin

## Good Operating Rule

If deployment succeeds but Garmin sync is not yet connected, the app is still usable as a dashboard and data model shell. Do not treat that as failure; report it as the next integration step.

