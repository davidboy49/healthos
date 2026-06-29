from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from healthos_api.schemas import JobStatus
from healthos_api.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/jobs", response_model=JobStatus)
def jobs(_: object = Depends(require_admin)) -> JobStatus:
    return JobStatus(queue="redis", status="configured", last_heartbeat=datetime.now(timezone.utc), scheduled_jobs=["garmin_incremental_sync", "daily_metric_refresh", "daily_agent_brief", "weekly_pattern_scan"])
