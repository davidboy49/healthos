from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from healthos_api.models import Activity, Confidence, DailyHealthSnapshot, DerivedMetric, HrvSample, ImportBatch, RawGarminPayload, SleepSession, StressSample


REQUIRED_COLUMNS = {"record_type", "start_time"}


@dataclass(frozen=True)
class FitnessSyncerRow:
    record_type: str
    start_time: datetime
    end_time: datetime | None
    value: float | None
    unit: str | None
    source_id: str | None
    raw: dict[str, str]


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_datetime(value: str | None) -> datetime:
    cleaned = _clean(value)
    if cleaned is None:
        raise ValueError("missing datetime")
    normalized = cleaned.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_float(value: str | None) -> float | None:
    cleaned = _clean(value)
    if cleaned is None:
        return None
    return float(cleaned)


def parse_fitnesssyncer_csv(content: str) -> tuple[list[FitnessSyncerRow], list[dict]]:
    reader = csv.DictReader(StringIO(content))
    if reader.fieldnames is None:
        return [], [{"row": 0, "error": "CSV has no header"}]

    normalized_headers = {header.strip().lower() for header in reader.fieldnames}
    missing = sorted(REQUIRED_COLUMNS - normalized_headers)
    if missing:
        return [], [{"row": 0, "error": f"Missing required columns: {', '.join(missing)}"}]

    parsed: list[FitnessSyncerRow] = []
    errors: list[dict] = []
    for index, raw_row in enumerate(reader, start=2):
        row = {str(key).strip().lower(): (value or "").strip() for key, value in raw_row.items()}
        try:
            parsed.append(
                FitnessSyncerRow(
                    record_type=(row.get("record_type") or "").lower(),
                    start_time=_parse_datetime(row.get("start_time")),
                    end_time=_parse_datetime(row.get("end_time")) if _clean(row.get("end_time")) else None,
                    value=_parse_float(row.get("value")),
                    unit=_clean(row.get("unit")),
                    source_id=_clean(row.get("source_id")),
                    raw=row,
                )
            )
        except Exception as exc:  # noqa: BLE001 - importer should collect row-level errors.
            errors.append({"row": index, "error": str(exc), "payload": row})
    return parsed, errors


def import_fitnesssyncer_csv(db: Session, user_id: UUID, content: str, original_filename: str, stored_path: str | None = None) -> ImportBatch:
    rows, errors = parse_fitnesssyncer_csv(content)
    batch = ImportBatch(
        user_id=user_id,
        source="fitnesssyncer_csv",
        original_filename=original_filename,
        stored_path=stored_path,
        total_rows=len(rows) + len(errors),
        errors=errors,
        status="processing",
    )
    db.add(batch)
    db.flush()

    processed = 0
    skipped = 0
    for row in rows:
        raw = RawGarminPayload(
            user_id=user_id,
            source="fitnesssyncer_csv",
            payload_type=row.record_type,
            external_id=row.source_id,
            payload=row.raw,
        )
        db.add(raw)
        db.flush()

        if _normalize_row(db, user_id, row, raw):
            processed += 1
        else:
            skipped += 1

    batch.processed_rows = processed
    batch.skipped_rows = skipped + len(errors)
    batch.status = "completed_with_errors" if errors or skipped else "completed"
    batch.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(batch)
    return batch


def import_fitnesssyncer_file(db: Session, user_id: UUID, path: Path) -> ImportBatch:
    content = path.read_text(encoding="utf-8-sig")
    return import_fitnesssyncer_csv(db, user_id, content, path.name, str(path))


def _normalize_row(db: Session, user_id: UUID, row: FitnessSyncerRow, raw: RawGarminPayload) -> bool:
    record_type = row.record_type
    if record_type == "sleep":
        duration = int(row.value or _duration_minutes(row.start_time, row.end_time))
        db.add(SleepSession(user_id=user_id, started_at=row.start_time, ended_at=row.end_time or row.start_time, duration_minutes=duration, score=_optional_raw_float(row, "score"), interruptions=_optional_raw_int(row, "interruptions"), stages={}, raw_payload_id=raw.id))
        _upsert_snapshot(db, user_id, row.start_time, sleep_score=_optional_raw_float(row, "score"))
        return True
    if record_type == "hrv":
        if row.value is None:
            return False
        db.add(HrvSample(user_id=user_id, measured_at=row.start_time, value_ms=row.value, baseline_ms=_optional_raw_float(row, "baseline"), deviation_pct=_optional_raw_float(row, "deviation_pct"), raw_payload_id=raw.id))
        return True
    if record_type == "stress":
        if row.value is None:
            return False
        db.add(StressSample(user_id=user_id, measured_at=row.start_time, stress_level=row.value, raw_payload_id=raw.id))
        _upsert_snapshot(db, user_id, row.start_time, stress_load=row.value)
        return True
    if record_type == "activity":
        db.add(Activity(user_id=user_id, external_id=row.source_id, sport_type=row.raw.get("sport_type") or "unknown", started_at=row.start_time, duration_minutes=int(row.value or _duration_minutes(row.start_time, row.end_time)), distance_meters=_optional_raw_float(row, "distance_meters"), training_effect=_optional_raw_float(row, "training_effect"), load_score=_optional_raw_float(row, "load_score"), gps_summary={}, raw_payload_id=raw.id))
        return True
    if record_type in {"steps", "resting_hr", "spo2"}:
        if row.value is None:
            return False
        db.add(DerivedMetric(user_id=user_id, name=record_type, value=row.value, unit=row.unit or "count", window_start=row.start_time, window_end=row.end_time or row.start_time, source_refs=[{"kind": "raw_payload", "id": str(raw.id), "label": f"FitnessSyncer {record_type}", "value": row.value}], confidence=Confidence.medium, explanation=f"Imported from FitnessSyncer CSV as {record_type}."))
        return True
    return False


def _duration_minutes(start: datetime, end: datetime | None) -> int:
    if end is None:
        return 0
    return max(0, int((end - start).total_seconds() / 60))


def _optional_raw_float(row: FitnessSyncerRow, key: str) -> float | None:
    return _parse_float(row.raw.get(key))


def _optional_raw_int(row: FitnessSyncerRow, key: str) -> int | None:
    value = _optional_raw_float(row, key)
    return int(value) if value is not None else None


def _upsert_snapshot(db: Session, user_id: UUID, measured_at: datetime, sleep_score: float | None = None, stress_load: float | None = None) -> None:
    snapshot_date = measured_at.date()
    snapshot = db.query(DailyHealthSnapshot).filter(DailyHealthSnapshot.user_id == user_id, DailyHealthSnapshot.snapshot_date == snapshot_date).one_or_none()
    if snapshot is None:
        snapshot = DailyHealthSnapshot(user_id=user_id, snapshot_date=snapshot_date, missing_data=[])
        db.add(snapshot)
    if sleep_score is not None:
        snapshot.sleep_score = sleep_score
    if stress_load is not None:
        snapshot.stress_load = stress_load
