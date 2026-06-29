# Operations Runbook

## Backup

Run nightly database dumps from the VPS and encrypt them before upload:

```bash
pg_dump "$DATABASE_URL" | age -r "$BACKUP_RECIPIENT" > "healthos-$(date +%F).sql.age"
```

## Restore drill

At least monthly, restore the latest backup into a clean database and run backend tests against it.

## Health checks

- API: `GET /healthz`
- Jobs: `GET /admin/jobs`
- Garmin sync: `GET /garmin/status`

