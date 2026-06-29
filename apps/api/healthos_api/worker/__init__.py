from celery import Celery

from healthos_api.config import get_settings

settings = get_settings()
celery_app = Celery("healthos", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "garmin-incremental-sync-hourly": {
        "task": "healthos_api.worker.tasks.sync_all_garmin_connections",
        "schedule": 60 * 60,
    },
    "daily-metric-refresh": {
        "task": "healthos_api.worker.tasks.refresh_daily_metrics",
        "schedule": 60 * 60 * 24,
    },
    "daily-agent-brief": {
        "task": "healthos_api.worker.tasks.run_daily_agent_briefs",
        "schedule": 60 * 60 * 24,
    },
}
celery_app.conf.timezone = "UTC"
