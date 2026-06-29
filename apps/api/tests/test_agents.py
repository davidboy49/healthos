import pytest

from healthos_api.schemas import EvidenceRef, HealthInsight
from healthos_api.services.agents import daily_coach_insight, validate_health_insight


def test_daily_coach_requires_evidence() -> None:
    with pytest.raises(ValueError):
        validate_health_insight(
            HealthInsight(
                title="No evidence",
                summary="This should fail.",
                evidence=[],
                confidence="low",
                severity="info",
                category="recovery",
                medicalDisclaimerRequired=False,
            )
        )


def test_safety_agent_blocks_medical_language() -> None:
    with pytest.raises(ValueError):
        validate_health_insight(
            HealthInsight(
                title="Diagnosis",
                summary="This attempts to diagnose a disease.",
                evidence=[EvidenceRef(kind="derived_metric", id="m1", label="HRV", value=-20)],
                confidence="medium",
                severity="important",
                category="recovery",
                medicalDisclaimerRequired=True,
            )
        )


def test_daily_coach_produces_evidence_backed_recommendation() -> None:
    insight = daily_coach_insight(82, "hard training available", [EvidenceRef(kind="snapshot", id="s1", label="Readiness", value=82)])
    assert insight.confidence == "high"
    assert insight.evidence[0].id == "s1"
    assert insight.recommendedAction == "hard training available"
