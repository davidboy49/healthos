import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from healthos_api.database import Base


class InsightCategory(str, enum.Enum):
    sleep = "sleep"
    recovery = "recovery"
    training = "training"
    stress = "stress"
    experiment = "experiment"


class Confidence(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Severity(str, enum.Enum):
    info = "info"
    watch = "watch"
    important = "important"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GarminConnection(Base):
    __tablename__ = "garmin_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    encrypted_access_token: Mapped[str] = mapped_column(Text)
    encrypted_refresh_token: Mapped[str] = mapped_column(Text)
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_backfill_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RawGarminPayload(Base):
    __tablename__ = "raw_garmin_payloads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(64), default="garmin_api")
    payload_type: Mapped[str] = mapped_column(String(80), index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    normalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("user_id", "payload_type", "external_id", name="uq_raw_payload_identity"),)


class DailyHealthSnapshot(Base):
    __tablename__ = "daily_health_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    readiness_score: Mapped[float | None] = mapped_column(Float)
    sleep_score: Mapped[float | None] = mapped_column(Float)
    hrv_status: Mapped[str | None] = mapped_column(String(64))
    stress_load: Mapped[float | None] = mapped_column(Float)
    training_recommendation: Mapped[str | None] = mapped_column(String(255))
    missing_data: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "snapshot_date", name="uq_daily_snapshot_user_date"),)


class SleepSession(Base):
    __tablename__ = "sleep_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    score: Mapped[float | None] = mapped_column(Float)
    interruptions: Mapped[int | None] = mapped_column(Integer)
    stages: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_payload_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("raw_garmin_payloads.id"))


class HrvSample(Base):
    __tablename__ = "hrv_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    value_ms: Mapped[float] = mapped_column(Float)
    baseline_ms: Mapped[float | None] = mapped_column(Float)
    deviation_pct: Mapped[float | None] = mapped_column(Float)
    raw_payload_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("raw_garmin_payloads.id"))


class StressSample(Base):
    __tablename__ = "stress_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    stress_level: Mapped[float] = mapped_column(Float)
    raw_payload_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("raw_garmin_payloads.id"))


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    sport_type: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    distance_meters: Mapped[float | None] = mapped_column(Float)
    training_effect: Mapped[float | None] = mapped_column(Float)
    load_score: Mapped[float | None] = mapped_column(Float)
    gps_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_payload_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("raw_garmin_payloads.id"))


class TrainingLoad(Base):
    __tablename__ = "training_loads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    load_date: Mapped[date] = mapped_column(Date, index=True)
    acute_load: Mapped[float] = mapped_column(Float)
    chronic_load: Mapped[float] = mapped_column(Float)
    ratio: Mapped[float | None] = mapped_column(Float)
    trend: Mapped[str] = mapped_column(String(64), default="stable")


class RecoveryState(Base):
    __tablename__ = "recovery_states"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    state_date: Mapped[date] = mapped_column(Date, index=True)
    readiness_score: Mapped[float] = mapped_column(Float)
    fatigue_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_intensity: Mapped[str] = mapped_column(String(80))


class ManualEvent(Base):
    __tablename__ = "manual_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    intensity: Mapped[float | None] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(Text)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class DerivedMetric(Base):
    __tablename__ = "derived_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(40))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_refs: Mapped[list[dict]] = mapped_column(JSON, default=list)
    confidence: Mapped[Confidence] = mapped_column(Enum(Confidence), default=Confidence.medium)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AiInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    summary: Mapped[str] = mapped_column(Text)
    evidence_refs: Mapped[list[dict]] = mapped_column(JSON, default=list)
    confidence: Mapped[Confidence] = mapped_column(Enum(Confidence), default=Confidence.medium)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.info)
    category: Mapped[InsightCategory] = mapped_column(Enum(InsightCategory))
    recommended_action: Mapped[str | None] = mapped_column(Text)
    medical_disclaimer_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    insight_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ai_insights.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(40), default="low")
    status: Mapped[str] = mapped_column(String(40), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    hypothesis: Mapped[str] = mapped_column(Text)
    intervention: Mapped[str] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    target_metrics: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="planned")
    results: Mapped[dict] = mapped_column(JSON, default=dict)


Index("ix_metrics_user_name_window", DerivedMetric.user_id, DerivedMetric.name, DerivedMetric.window_start, DerivedMetric.window_end)


