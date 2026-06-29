from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from healthos_api.config import get_settings
from healthos_api.database import get_db
from healthos_api.models import ImportBatch, User
from healthos_api.schemas import ImportBatchResponse, LocalImportRequest
from healthos_api.security import get_current_user
from healthos_api.services.fitnesssyncer import import_fitnesssyncer_csv, import_fitnesssyncer_file

router = APIRouter(prefix="/imports", tags=["imports"])


def _response(batch: ImportBatch) -> ImportBatchResponse:
    return ImportBatchResponse(
        id=batch.id,
        source=batch.source,
        original_filename=batch.original_filename,
        stored_path=batch.stored_path,
        status=batch.status,
        total_rows=batch.total_rows,
        processed_rows=batch.processed_rows,
        skipped_rows=batch.skipped_rows,
        errors=batch.errors,
        created_at=batch.created_at,
        completed_at=batch.completed_at,
    )


def _import_root() -> Path:
    root = Path(get_settings().import_storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


@router.post("/fitnesssyncer", response_model=ImportBatchResponse)
async def upload_fitnesssyncer_csv(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ImportBatchResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="FitnessSyncer import requires a CSV file")

    content_bytes = await file.read()
    content = content_bytes.decode("utf-8-sig")
    root = _import_root()
    stored_path = root / file.filename
    stored_path.write_bytes(content_bytes)
    batch = import_fitnesssyncer_csv(db, user.id, content, file.filename, str(stored_path))
    return _response(batch)


@router.post("/fitnesssyncer/local", response_model=ImportBatchResponse)
def import_local_fitnesssyncer_csv(payload: LocalImportRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ImportBatchResponse:
    root = _import_root()
    path = Path(payload.path)
    candidate = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if root not in candidate.parents and candidate != root:
        raise HTTPException(status_code=400, detail="Local imports must be inside IMPORT_STORAGE_DIR")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Import file not found")
    if candidate.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="FitnessSyncer local import requires a CSV file")
    batch = import_fitnesssyncer_file(db, user.id, candidate)
    return _response(batch)


@router.get("", response_model=list[ImportBatchResponse])
def list_imports(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ImportBatchResponse]:
    batches = db.query(ImportBatch).filter(ImportBatch.user_id == user.id).order_by(ImportBatch.created_at.desc()).limit(50).all()
    return [_response(batch) for batch in batches]
