from backend.services.alert_engine import generate_alert


# =====================================================
# EXPERIMENT 04
# ALERT ENGINE EVALUATION
# =====================================================


def test_low_risk_alert():
    """
    Low risk should generate a low-severity alert.
    """

    result = generate_alert(
        risk_score=20.0,
        risk_level="low",
        risk_factors=[
            "Low document similarity"
        ],
    )

    assert result["alert_type"] == "low_risk"
    assert result["severity"] == "low"
    assert result["status"] == "open"

    assert (
        "Low examination security risk"
        in result["message"]
    )


def test_medium_risk_alert():
    """
    Medium risk should generate a moderate-risk alert.
    """

    result = generate_alert(
        risk_score=50.0,
        risk_level="medium",
        risk_factors=[
            "Moderate document similarity"
        ],
    )

    assert (
        result["alert_type"]
        == "moderate_risk"
    )

    assert result["severity"] == "medium"
    assert result["status"] == "open"

    assert (
        "Moderate examination security risk"
        in result["message"]
    )


def test_high_risk_alert():
    """
    High risk should generate a high-risk alert.
    """

    result = generate_alert(
        risk_score=75.0,
        risk_level="high",
        risk_factors=[
            "High document similarity"
        ],
    )

    assert result["alert_type"] == "high_risk"
    assert result["severity"] == "high"
    assert result["status"] == "open"

    assert (
        "High examination security risk"
        in result["message"]
    )


def test_critical_risk_alert():
    """
    Critical risk should generate a critical alert.
    """

    result = generate_alert(
        risk_score=95.0,
        risk_level="critical",
        risk_factors=[
            "Very high document similarity"
        ],
    )

    assert (
        result["alert_type"]
        == "critical_risk"
    )

    assert result["severity"] == "critical"
    assert result["status"] == "open"

    assert (
        "Critical examination security risk"
        in result["message"]
    )


def test_alert_structure():
    """
    Every generated alert should contain
    the required response fields.
    """

    risk_levels = [
        "low",
        "medium",
        "high",
        "critical",
    ]

    for level in risk_levels:

        result = generate_alert(
            risk_score=50.0,
            risk_level=level,
            risk_factors=[],
        )

        assert isinstance(result, dict)

        assert "alert_type" in result
        assert "severity" in result
        assert "message" in result
        assert "status" in result

        assert result["status"] == "open"


def test_alert_severity_matches_risk_level():
    """
    Alert severity should correspond directly
    to the supplied risk level.
    """

    expected = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "critical": "critical",
    }

    for risk_level, expected_severity in expected.items():

        result = generate_alert(
            risk_score=50.0,
            risk_level=risk_level,
            risk_factors=[],
        )

        assert (
            result["severity"]
            == expected_severity
        )


def test_alert_type_matches_risk_level():
    """
    Verify the mapping between risk level
    and alert type.
    """

    expected = {
        "low": "low_risk",
        "medium": "moderate_risk",
        "high": "high_risk",
        "critical": "critical_risk",
    }

    for risk_level, expected_type in expected.items():

        result = generate_alert(
            risk_score=50.0,
            risk_level=risk_level,
            risk_factors=[],
        )

        assert (
            result["alert_type"]
            == expected_type
        )


def test_alert_message_is_explainable():
    """
    Every alert should contain a meaningful
    human-readable message.
    """

    for risk_level in [
        "low",
        "medium",
        "high",
        "critical",
    ]:

        result = generate_alert(
            risk_score=50.0,
            risk_level=risk_level,
            risk_factors=[],
        )

        message = result["message"]

        assert isinstance(
            message,
            str,
        )

        assert len(
            message.strip()
        ) > 20