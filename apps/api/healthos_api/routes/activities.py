from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import Activity, User
from healthos_api.schemas import ActivityResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivityResponse])
def activities(from_date: datetime = Query(alias="from"), to: datetime = Query(), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ActivityResponse]:
    rows = db.query(Activity).filter(Activity.user_id == user.id, Activity.started_at >= from_date, Activity.started_at <= to).order_by(Activity.started_at.desc()).all()
    return [ActivityResponse(id=row.id, sport_type=row.sport_type, started_at=row.started_at, duration_minutes=row.duration_minutes, distance_meters=row.distance_meters, training_effect=row.training_effect, load_score=row.load_score) for row in rows]
