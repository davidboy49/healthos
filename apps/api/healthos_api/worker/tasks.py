from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from healthos_api.database import SessionLocal
from healthos_api.models import AiInsight, Confidence, DailyHealthSnapshot, DerivedMetric, GarminConnection, InsightCategory, Severity, User
from healthos_api.schemas import EvidenceRef
from healthos_api.services.agents import daily_coach_insight
from healthos_api.services.metrics import recommended_intensity
from healthos_api.worker import celery_app


@celery_app.task(name="healthos_api.worker.tasks.sync_garmin_for_user")
def sync_garmin_for_user(user_id: str) -> dict:
    db = SessionLocal()
    try:
        connection = db.query(GarminConnection).filter(GarminConnection.user_id == UUID(user_id)).one_or_none()
        if connection is None:
            return {"status": "skipped", "reason": "no_garmin_connection"}
        connection.last_sync_at = datetime.now(timezone.utc)
        connection.last_error = None
        db.commit()
        return {"status": "accepted", "user_id": user_id}
    finally:
        db.close()


@celery_app.task(name="healthos_api.worker.tasks.sync_all_garmin_connections")
def sync_all_garmin_connections() -> dict:
    db = SessionLocal()
    try:
        ids = [str(row.user_id) for row in db.query(GarminConnection).all()]
    finally:
        db.close()
    for user_id in ids:
        sync_garmin_for_user.delay(user_id)
    return {"scheduled": len(ids)}


@celery_app.task(name="healthos_api.worker.tasks.refresh_daily_metrics")
def refresh_daily_metrics() -> dict:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            snapshot = db.query(DailyHealthSnapshot).filter(DailyHealthSnapshot.user_id == user.id, DailyHealthSnapshot.snapshot_date == date.today()).one_or_none()
            if snapshot is None:
                snapshot = DailyHealthSnapshot(user_id=user.id, snapshot_date=date.today(), readiness_score=None, missing_data=["sleep", "hrv", "stress", "training_load"])
                db.add(snapshot)
        db.commit()
        return {"refreshed_users": len(users)}
    finally:
        db.close()


@celery_app.task(name="healthos_api.worker.tasks.run_daily_agent_briefs")
def run_daily_agent_briefs() -> dict:
    db = SessionLocal()
    try:
        count = 0
        for user in db.query(User).all():
            snapshot = db.query(DailyHealthSnapshot).filter(DailyHealthSnapshot.user_id == user.id, DailyHealthSnapshot.snapshot_date == date.today()).one_or_none()
            evidence = [EvidenceRef(kind="snapshot", id=str(snapshot.id), label="Daily readiness", value=snapshot.readiness_score)] if snapshot else [EvidenceRef(kind="snapshot", id="missing", label="Missing daily snapshot")]
            insight = daily_coach_insight(snapshot.readiness_score if snapshot else None, snapshot.training_recommendation if snapshot else None, evidence)
            db.add(AiInsight(user_id=user.id, title=insight.title, summary=insight.summary, evidence_refs=[item.model_dump() for item in insight.evidence], confidence=Confidence(insight.confidence), severity=Severity(insight.severity), category=InsightCategory(insight.category), recommended_action=insight.recommendedAction, medical_disclaimer_required=insight.medicalDisclaimerRequired))
            count += 1
        db.commit()
        return {"created_insights": count}
    finally:
        db.close()
