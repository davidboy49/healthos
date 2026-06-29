from datetime import datetime, timezone

from healthos_api.services.metrics import fatigue_flags, readiness_score, sleep_debt_minutes, training_load_ratio


def test_sleep_debt_minutes_counts_only_shortfall() -> None:
    assert sleep_debt_minutes([480, 420, 510, 390]) == 150


def test_training_load_ratio_handles_missing_chronic_load() -> None:
    assert training_load_ratio(250, 0) is None
    assert training_load_ratio(250, 500) == 0.5


def test_readiness_score_is_bounded() -> None:
    assert readiness_score(10, -90, 50, 100, 2.5) >= 0
    assert readiness_score(100, 90, -10, 0, 0.8) <= 100


def test_fatigue_flags_detect_combined_recovery_risk() -> None:
    flags = fatigue_flags(hrv_deviation_pct=-15, resting_hr_deviation_pct=9, sleep_debt=180, stress_load=75)
    assert flags == ["low_hrv", "elevated_resting_hr", "sleep_debt", "high_stress"]
