from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import AiInsight, InsightCategory, User
from healthos_api.schemas import EvidenceRef, InsightResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=list[InsightResponse])
def insights(category: InsightCategory | None = None, from_date: datetime | None = Query(default=None, alias="from"), to: datetime | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[InsightResponse]:
    query = db.query(AiInsight).filter(AiInsight.user_id == user.id)
    if category is not None:
        query = query.filter(AiInsight.category == category)
    if from_date is not None:
        query = query.filter(AiInsight.created_at >= from_date)
    if to is not None:
        query = query.filter(AiInsight.created_at <= to)
    rows = query.order_by(AiInsight.created_at.desc()).all()
    return [InsightResponse(id=row.id, title=row.title, summary=row.summary, evidence=[EvidenceRef(**item) for item in row.evidence_refs], confidence=row.confidence.value, severity=row.severity.value, category=row.category.value, recommendedAction=row.recommended_action, medicalDisclaimerRequired=row.medical_disclaimer_required, created_at=row.created_at) for row in rows]
