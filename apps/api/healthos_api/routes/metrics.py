from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import DerivedMetric, User
from healthos_api.routes.health import _metric_response
from healthos_api.schemas import MetricResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/{name}", response_model=list[MetricResponse])
def metrics(name: str, from_date: datetime = Query(alias="from"), to: datetime = Query(), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[MetricResponse]:
    rows = db.query(DerivedMetric).filter(
        DerivedMetric.user_id == user.id,
        DerivedMetric.name == name,
        DerivedMetric.window_start >= from_date,
        DerivedMetric.window_end <= to,
    ).order_by(DerivedMetric.window_start).all()
    return [_metric_response(row) for row in rows]
