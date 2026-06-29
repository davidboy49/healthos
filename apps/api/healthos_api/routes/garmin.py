from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import GarminConnection, User
from healthos_api.schemas import GarminConnectRequest, GarminStatusResponse, SyncResponse
from healthos_api.security import get_current_user
from healthos_api.services.garmin import GarminClient, upsert_connection
from healthos_api.worker.tasks import sync_garmin_for_user

router = APIRouter(prefix="/garmin", tags=["garmin"])


@router.post("/connect", response_model=GarminStatusResponse)
async def connect_garmin(payload: GarminConnectRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GarminStatusResponse:
    token_payload = await GarminClient().exchange_code(payload.code, payload.redirect_uri)
    connection = upsert_connection(db, user.id, token_payload)
    return GarminStatusResponse(connected=True, scopes=connection.scopes, last_sync_at=connection.last_sync_at, last_error=connection.last_error)


@router.get("/status", response_model=GarminStatusResponse)
def garmin_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> GarminStatusResponse:
    connection = db.query(GarminConnection).filter(GarminConnection.user_id == user.id).one_or_none()
    if connection is None:
        return GarminStatusResponse(connected=False)
    return GarminStatusResponse(connected=True, scopes=connection.scopes, last_sync_at=connection.last_sync_at, last_error=connection.last_error)


@router.post("/sync", response_model=SyncResponse)
def garmin_sync(user: User = Depends(get_current_user)) -> SyncResponse:
    task = sync_garmin_for_user.delay(str(user.id))
    return SyncResponse(accepted=True, job_id=task.id)
