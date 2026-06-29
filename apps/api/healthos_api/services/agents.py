from healthos_api.schemas import EvidenceRef, HealthInsight


MEDICAL_BLOCKLIST = (
    "diagnose",
    "diagnosis",
    "prescribe",
    "medication",
    "disease",
    "emergency",
    "heart attack",
    "stroke",
)


def validate_health_insight(insight: HealthInsight) -> HealthInsight:
    if not insight.evidence:
        raise ValueError("Health insights require at least one evidence reference")
    text = f"{insight.title} {insight.summary} {insight.recommendedAction or ''}".lower()
    if any(term in text for term in MEDICAL_BLOCKLIST):
        raise ValueError("Insight contains medical diagnosis or treatment language")
    return insight


def daily_coach_insight(readiness: float | None, recommendation: str | None, evidence: list[EvidenceRef]) -> HealthInsight:
    if readiness is None:
        title = "Readiness needs more data"
        summary = "Garmin data is incomplete, so today's coaching should stay conservative."
        severity = "watch"
        confidence = "low"
        action = "Check Garmin sync status before making training decisions."
    elif readiness >= 78:
        title = "Good recovery window"
        summary = "Your computed readiness is strong and no major fatigue flags are present."
        severity = "info"
        confidence = "high"
        action = recommendation or "A quality training session is reasonable if you feel good."
    elif readiness >= 55:
        title = "Use a controlled training day"
        summary = "Your signals are mixed, so the best move is productive work without digging a recovery hole."
        severity = "watch"
        confidence = "medium"
        action = recommendation or "Keep intensity moderate and watch perceived effort."
    else:
        title = "Recovery should lead today"
        summary = "Your readiness score is low enough that extra intensity may cost more than it gives back."
        severity = "important"
        confidence = "medium"
        action = recommendation or "Prioritize sleep, hydration, mobility, or easy aerobic work."

    return validate_health_insight(
        HealthInsight(
            title=title,
            summary=summary,
            evidence=evidence,
            confidence=confidence,
            severity=severity,
            category="recovery",
            recommendedAction=action,
            medicalDisclaimerRequired=False,
        )
    )

