# Personal Health OS

Self-hosted, evidence-first health platform for Garmin data, deterministic metrics, Hermes-style agents, and a private dashboard.

## What is included

- `apps/api` - FastAPI backend, SQLAlchemy models, Garmin sync facade, metric engine, Hermes agent contracts.
- `apps/web` - Next.js dashboard shell with premium health-command-center UX.
- `infra` - Docker Compose, Caddy reverse proxy, and database bootstrap.
- `docs` - Implementation notes and operational runbooks.

## Quick start

1. Copy `.env.example` to `.env`.
2. Fill in secrets and Garmin OAuth credentials.
3. Run:

```bash
docker compose up --build
```

The default local URLs are:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Architecture

```text
Garmin API
  -> ingestion worker
  -> raw health store
  -> normalized health models
  -> derived metrics engine
  -> Hermes agent layer
  -> recommendations and insights
  -> Next.js dashboard
```

AI outputs are required to cite stored metrics or source records. The platform is for wellness and performance guidance, not diagnosis or treatment.

## FitnessSyncer Imports

Garmin API access is optional. The current preferred automation path is FitnessSyncer CSV export plus n8n. See docs/n8n/fitnesssyncer-import.md and samples/fitnesssyncer_mock.csv.
