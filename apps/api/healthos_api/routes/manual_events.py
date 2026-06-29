from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import ManualEvent, User
from healthos_api.schemas import ManualEventCreate, ManualEventResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/manual-events", tags=["manual-events"])


@router.post("", response_model=ManualEventResponse)
def create_manual_event(payload: ManualEventCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ManualEventResponse:
    event = ManualEvent(user_id=user.id, event_type=payload.event_type, occurred_at=payload.occurred_at, intensity=payload.intensity, note=payload.note, event_metadata=payload.event_metadata)
    db.add(event)
    db.commit()
    db.refresh(event)
    return ManualEventResponse(id=event.id, event_type=event.event_type, occurred_at=event.occurred_at, intensity=event.intensity, note=event.note, event_metadata=event.event_metadata)
