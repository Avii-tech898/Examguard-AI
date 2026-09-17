def generate_alert(
    risk_score: float,
    risk_level: str,
    risk_factors: list
) -> dict:
    """
    Alert Engine v2

    Generates explainable alerts from
    Risk Engine V1 / V2 results.
    """

    # -----------------------------
    # Critical Risk
    # -----------------------------
    if risk_level == "critical":
        return {
            "alert_type": "critical_risk",
            "severity": "critical",
            "message": (
                "Critical examination security risk detected. "
                "Immediate manual investigation required."
            ),
            "status": "open"
        }

    # -----------------------------
    # High Risk
    # -----------------------------
    if risk_level == "high":
        return {
            "alert_type": "high_risk",
            "severity": "high",
            "message": (
                "High examination security risk detected. "
                "Similarity and document structure require review."
            ),
            "status": "open"
        }

    # -----------------------------
    # Medium Risk
    # -----------------------------
    if risk_level == "medium":
        return {
            "alert_type": "moderate_risk",
            "severity": "medium",
            "message": (
                "Moderate examination security risk detected. "
                "Further verification is recommended."
            ),
            "status": "open"
        }

    # -----------------------------
    # Low Risk
    # -----------------------------
    return {
        "alert_type": "low_risk",
        "severity": "low",
        "message": (
            "Low examination security risk detected. "
            "No immediate action required."
        ),
        "status": "open"
    }