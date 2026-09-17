from typing import Any


# =====================================================
# RISK ENGINE V1
# =====================================================

def calculate_risk(similarity_score: float) -> dict:
    """
    Rule-based Risk Engine v1.

    This is the original baseline model.
    It uses document similarity as the
    primary suspiciousness signal.

    IMPORTANT:
    Keep this function unchanged in behavior
    for baseline comparison.
    """

    if similarity_score < 30:
        risk_score = 20.0
        risk_level = "low"
        risk_factors = [
            "Low document similarity"
        ]

    elif similarity_score < 60:
        risk_score = 50.0
        risk_level = "medium"
        risk_factors = [
            "Moderate document similarity"
        ]

    elif similarity_score < 80:
        risk_score = 75.0
        risk_level = "high"
        risk_factors = [
            "High document similarity"
        ]

    else:
        risk_score = 95.0
        risk_level = "critical"
        risk_factors = [
            "Very high document similarity"
        ]

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "model_version": "risk-rule-v1"
    }


# =====================================================
# HELPER
# =====================================================

def _safe_float(
    value: Any,
    default: float = 0.0
) -> float:
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


# =====================================================
# RISK ENGINE V2
# =====================================================

def calculate_feature_based_risk(
    features: dict[str, Any]
) -> dict:
    """
    Feature-aware rule-based Risk Engine v2.

    This version uses multiple document features
    instead of relying only on similarity.

    Features currently considered:

    - similarity_score
    - word_count_difference_ratio
    - sentence_count_difference_ratio
    - character_count_difference_ratio
    - unique_word_difference_ratio

    The system remains explainable and deterministic.
    """

    similarity_score = _safe_float(
        features.get("similarity_score")
    )

    word_diff_ratio = _safe_float(
        features.get(
            "word_count_difference_ratio"
        )
    )

    sentence_diff_ratio = _safe_float(
        features.get(
            "sentence_count_difference_ratio"
        )
    )

    character_diff_ratio = _safe_float(
        features.get(
            "character_count_difference_ratio"
        )
    )

    unique_word_diff_ratio = _safe_float(
        features.get(
            "unique_word_difference_ratio"
        )
    )


    # =====================================================
    # STARTING SCORE
    # =====================================================

    risk_score = 0.0

    risk_factors = []


    # =====================================================
    # SIMILARITY CONTRIBUTION
    # =====================================================

    if similarity_score >= 80:

        risk_score += 60

        risk_factors.append(
            "Very high document similarity"
        )

    elif similarity_score >= 60:

        risk_score += 45

        risk_factors.append(
            "High document similarity"
        )

    elif similarity_score >= 40:

        risk_score += 30

        risk_factors.append(
            "Moderate-high document similarity"
        )

    elif similarity_score >= 30:

        risk_score += 15

        risk_factors.append(
            "Moderate document similarity"
        )

    else:

        risk_score += 5

        risk_factors.append(
            "Low document similarity"
        )


    # =====================================================
    # WORD COUNT DIFFERENCE
    # =====================================================

    if word_diff_ratio <= 0.10:

        risk_score += 15

        risk_factors.append(
            "Very similar word count"
        )

    elif word_diff_ratio <= 0.25:

        risk_score += 8

        risk_factors.append(
            "Similar word count"
        )


    # =====================================================
    # SENTENCE COUNT DIFFERENCE
    # =====================================================

    if sentence_diff_ratio <= 0.10:

        risk_score += 10

        risk_factors.append(
            "Very similar sentence structure"
        )

    elif sentence_diff_ratio <= 0.25:

        risk_score += 5

        risk_factors.append(
            "Similar sentence structure"
        )


    # =====================================================
    # CHARACTER COUNT DIFFERENCE
    # =====================================================

    if character_diff_ratio <= 0.10:

        risk_score += 10

        risk_factors.append(
            "Very similar document length"
        )

    elif character_diff_ratio <= 0.25:

        risk_score += 5

        risk_factors.append(
            "Similar document length"
        )


    # =====================================================
    # UNIQUE WORD DIFFERENCE
    # =====================================================

    if unique_word_diff_ratio <= 0.10:

        risk_score += 5

        risk_factors.append(
            "Very similar vocabulary size"
        )

    elif unique_word_diff_ratio <= 0.25:

        risk_score += 3

        risk_factors.append(
            "Similar vocabulary size"
        )


    # =====================================================
    # NORMALIZE SCORE
    # =====================================================

    risk_score = min(
        round(risk_score, 2),
        100.0
    )


    # =====================================================
    # RISK LEVEL
    # =====================================================

    if risk_score < 30:

        risk_level = "low"

    elif risk_score < 60:

        risk_level = "medium"

    elif risk_score < 80:

        risk_level = "high"

    else:

        risk_level = "critical"


    # =====================================================
    # FALLBACK FACTOR
    # =====================================================

    if not risk_factors:

        risk_factors.append(
            "No significant suspicious pattern detected"
        )


    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "model_version": "risk-rule-v2"
    }