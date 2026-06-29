from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float
    unit: str
    confidence: str
    explanation: str
    source_refs: list[dict]


def rolling_average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def sleep_debt_minutes(sleep_minutes: list[int], target_minutes: int = 480) -> int:
    return sum(max(target_minutes - minutes, 0) for minutes in sleep_minutes)


def percent_deviation(value: float, baseline: float | None) -> float | None:
    if baseline is None or baseline == 0:
        return None
    return ((value - baseline) / baseline) * 100


def training_load_ratio(acute_load: float, chronic_load: float) -> float | None:
    if chronic_load <= 0:
        return None
    return acute_load / chronic_load


def readiness_score(
    sleep_score: float | None,
    hrv_deviation_pct: float | None,
    resting_hr_deviation_pct: float | None,
    stress_load: float | None,
    training_ratio: float | None,
) -> float:
    score = 80.0
    if sleep_score is not None:
        score += (sleep_score - 75) * 0.25
    if hrv_deviation_pct is not None:
        score += max(min(hrv_deviation_pct, 15), -25) * 0.6
    if resting_hr_deviation_pct is not None and resting_hr_deviation_pct > 0:
        score -= min(resting_hr_deviation_pct, 20) * 0.8
    if stress_load is not None:
        score -= max(stress_load - 50, 0) * 0.25
    if training_ratio is not None and training_ratio > 1.3:
        score -= min((training_ratio - 1.3) * 25, 15)
    return round(max(0, min(100, score)), 1)


def fatigue_flags(
    hrv_deviation_pct: float | None,
    resting_hr_deviation_pct: float | None,
    sleep_debt: int,
    stress_load: float | None,
) -> list[str]:
    flags: list[str] = []
    if hrv_deviation_pct is not None and hrv_deviation_pct <= -12:
        flags.append("low_hrv")
    if resting_hr_deviation_pct is not None and resting_hr_deviation_pct >= 8:
        flags.append("elevated_resting_hr")
    if sleep_debt >= 120:
        flags.append("sleep_debt")
    if stress_load is not None and stress_load >= 70:
        flags.append("high_stress")
    return flags


def recommended_intensity(readiness: float, flags: list[str]) -> str:
    if readiness >= 78 and not flags:
        return "hard training available"
    if readiness >= 62 and len(flags) <= 1:
        return "moderate training"
    if readiness >= 45:
        return "easy aerobic or mobility"
    return "recovery priority"


def metric_window_ref(kind: str, record_id: str, label: str, value: float | str | None) -> dict:
    return {"kind": kind, "id": record_id, "label": label, "value": value}


def build_sleep_debt_metric(window_start: datetime, window_end: datetime, sleep_minutes: list[int]) -> MetricResult:
    debt = sleep_debt_minutes(sleep_minutes)
    return MetricResult(
        name="sleep_debt_7d",
        value=float(debt),
        unit="minutes",
        confidence="high" if len(sleep_minutes) >= 5 else "medium",
        explanation=f"Total missed sleep versus an 8 hour target across {len(sleep_minutes)} recorded nights.",
        source_refs=[{"kind": "sleep_sessions", "id": "window", "label": f"{window_start.date()} to {window_end.date()}"}],
    )

