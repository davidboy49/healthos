from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
Severity = Literal["info", "watch", "important"]
InsightCategory = Literal["sleep", "recovery", "training", "stress", "experiment"]


class EvidenceRef(BaseModel):
    kind: Literal["derived_metric", "raw_payload", "activity", "manual_event", "snapshot"]
    id: str
    label: str
    value: float | str | None = None


class HealthInsight(BaseModel):
    title: str
    summary: str
    evidence: list[EvidenceRef] = Field(min_length=1)
    confidence: Confidence
    severity: Severity
    category: InsightCategory
    recommendedAction: str | None = None
    medicalDisclaimerRequired: bool = False


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: UUID
    email: str
    is_admin: bool


class GarminConnectRequest(BaseModel):
    code: str
    redirect_uri: str


class GarminStatusResponse(BaseModel):
    connected: bool
    scopes: list[str] = []
    last_sync_at: datetime | None = None
    last_error: str | None = None


class SyncResponse(BaseModel):
    accepted: bool
    job_id: str


class MetricResponse(BaseModel):
    id: UUID
    name: str
    value: float
    unit: str
    window_start: datetime
    window_end: datetime
    confidence: Confidence
    explanation: str
    source_refs: list[dict]


class TodayResponse(BaseModel):
    date: date
    readiness_score: float | None
    sleep_score: float | None
    hrv_status: str | None
    stress_load: float | None
    training_recommendation: str | None
    missing_data: list[str]
    top_insight: HealthInsight | None
    metrics: list[MetricResponse]


class TimelineItem(BaseModel):
    date: date
    readiness_score: float | None
    sleep_score: float | None
    stress_load: float | None
    missing_data: list[str]


class ActivityResponse(BaseModel):
    id: UUID
    sport_type: str
    started_at: datetime
    duration_minutes: int
    distance_meters: float | None
    training_effect: float | None
    load_score: float | None


class InsightResponse(HealthInsight):
    id: UUID
    created_at: datetime


class RecommendationUpdate(BaseModel):
    status: Literal["open", "accepted", "dismissed", "completed"]


class ManualEventCreate(BaseModel):
    event_type: Literal["caffeine", "alcohol", "illness", "soreness", "mood", "travel", "supplement", "other"]
    occurred_at: datetime
    intensity: float | None = Field(default=None, ge=0, le=10)
    note: str | None = None
    event_metadata: dict = Field(default_factory=dict)


class ManualEventResponse(ManualEventCreate):
    id: UUID


class ExperimentCreate(BaseModel):
    name: str
    hypothesis: str
    intervention: str
    start_date: date
    end_date: date | None = None
    target_metrics: list[str] = []


class ExperimentResponse(ExperimentCreate):
    id: UUID
    status: str
    results: dict


class JobStatus(BaseModel):
    queue: str
    status: str
    last_heartbeat: datetime
    scheduled_jobs: list[str]



class ImportBatchResponse(BaseModel):
    id: UUID
    source: str
    original_filename: str
    stored_path: str | None
    status: str
    total_rows: int
    processed_rows: int
    skipped_rows: int
    errors: list[dict]
    created_at: datetime
    completed_at: datetime | None


class LocalImportRequest(BaseModel):
    path: str
