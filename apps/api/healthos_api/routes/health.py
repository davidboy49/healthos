from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import AiInsight, DailyHealthSnapshot, DerivedMetric, User
from healthos_api.schemas import EvidenceRef, HealthInsight, MetricResponse, TimelineItem, TodayResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/health", tags=["health"])


def _metric_response(metric: DerivedMetric) -> MetricResponse:
    return MetricResponse(
        id=metric.id,
        name=metric.name,
        value=metric.value,
        unit=metric.unit,
        window_start=metric.window_start,
        window_end=metric.window_end,
        confidence=metric.confidence.value,
        explanation=metric.explanation,
        source_refs=metric.source_refs,
    )


def _insight_response(insight: AiInsight | None) -> HealthInsight | None:
    if insight is None:
        return None
    return HealthInsight(
        title=insight.title,
        summary=insight.summary,
        evidence=[EvidenceRef(**item) for item in insight.evidence_refs],
        confidence=insight.confidence.value,
        severity=insight.severity.value,
        category=insight.category.value,
        recommendedAction=insight.recommended_action,
        medicalDisclaimerRequired=insight.medical_disclaimer_required,
    )


@router.get("/today", response_model=TodayResponse)
def today(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> TodayResponse:
    today_date = date.today()
    snapshot = db.query(DailyHealthSnapshot).filter(DailyHealthSnapshot.user_id == user.id, DailyHealthSnapshot.snapshot_date == today_date).one_or_none()
    latest_insight = db.query(AiInsight).filter(AiInsight.user_id == user.id).order_by(desc(AiInsight.created_at)).first()
    metrics = db.query(DerivedMetric).filter(DerivedMetric.user_id == user.id).order_by(desc(DerivedMetric.created_at)).limit(8).all()
    return TodayResponse(
        date=today_date,
        readiness_score=snapshot.readiness_score if snapshot else None,
        sleep_score=snapshot.sleep_score if snapshot else None,
        hrv_status=snapshot.hrv_status if snapshot else None,
        stress_load=snapshot.stress_load if snapshot else None,
        training_recommendation=snapshot.training_recommendation if snapshot else None,
        missing_data=snapshot.missing_data if snapshot else ["daily_snapshot"],
        top_insight=_insight_response(latest_insight),
        metrics=[_metric_response(metric) for metric in metrics],
    )


@router.get("/timeline", response_model=list[TimelineItem])
def timeline(from_date: date = Query(alias="from"), to: date = Query(), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[TimelineItem]:
    rows = db.query(DailyHealthSnapshot).filter(
        DailyHealthSnapshot.user_id == user.id,
        DailyHealthSnapshot.snapshot_date >= from_date,
        DailyHealthSnapshot.snapshot_date <= to,
    ).order_by(DailyHealthSnapshot.snapshot_date).all()
    return [TimelineItem(date=row.snapshot_date, readiness_score=row.readiness_score, sleep_score=row.sleep_score, stress_load=row.stress_load, missing_data=row.missing_data) for row in rows]
