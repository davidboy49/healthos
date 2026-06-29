from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import Recommendation, User
from healthos_api.schemas import RecommendationUpdate
from healthos_api.security import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.patch("/{recommendation_id}")
def update_recommendation(recommendation_id: UUID, payload: RecommendationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id, Recommendation.user_id == user.id).one_or_none()
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendation.status = payload.status
    db.commit()
    return {"id": str(recommendation.id), "status": recommendation.status}
