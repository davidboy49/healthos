from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from healthos_api.database import get_db
from healthos_api.models import Experiment, User
from healthos_api.schemas import ExperimentCreate, ExperimentResponse
from healthos_api.security import get_current_user

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentResponse)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExperimentResponse:
    experiment = Experiment(user_id=user.id, name=payload.name, hypothesis=payload.hypothesis, intervention=payload.intervention, start_date=payload.start_date, end_date=payload.end_date, target_metrics=payload.target_metrics)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return ExperimentResponse(id=experiment.id, name=experiment.name, hypothesis=experiment.hypothesis, intervention=experiment.intervention, start_date=experiment.start_date, end_date=experiment.end_date, target_metrics=experiment.target_metrics, status=experiment.status, results=experiment.results)


@router.get("/{experiment_id}/results", response_model=ExperimentResponse)
def experiment_results(experiment_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ExperimentResponse:
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == user.id).one_or_none()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse(id=experiment.id, name=experiment.name, hypothesis=experiment.hypothesis, intervention=experiment.intervention, start_date=experiment.start_date, end_date=experiment.end_date, target_metrics=experiment.target_metrics, status=experiment.status, results=experiment.results)
