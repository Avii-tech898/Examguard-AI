from backend.services.risk_engine import (
    calculate_risk,
    calculate_feature_based_risk,
)


# =====================================================
# EXPERIMENT 02
# RISK ENGINE V1 vs V2
# =====================================================


def run_v1_v2_comparison(features):
    """
    Run both Risk Engine V1 and Risk Engine V2
    on the same similarity/features scenario.
    """

    similarity_score = features["similarity_score"]

    risk_v1 = calculate_risk(
        similarity_score
    )

    risk_v2 = calculate_feature_based_risk(
        features
    )

    return {
        "v1": risk_v1,
        "v2": risk_v2,
        "score_difference": round(
            risk_v2["risk_score"]
            - risk_v1["risk_score"],
            2,
        ),
    }


# =====================================================
# CASE 1
# LOW SIMILARITY
# =====================================================

def test_case_1_low_similarity():
    features = {
        "similarity_score": 20.0,
        "word_count_difference_ratio": 0.80,
        "sentence_count_difference_ratio": 0.80,
        "character_count_difference_ratio": 0.80,
        "unique_word_difference_ratio": 0.80,
    }

    result = run_v1_v2_comparison(
        features
    )

    assert result["v1"]["risk_level"] == "low"
    assert result["v2"]["risk_level"] == "low"

    assert (
        result["v1"]["risk_score"]
        == 20.0
    )


# =====================================================
# CASE 2
# MODERATE SIMILARITY
# =====================================================

def test_case_2_moderate_similarity():
    features = {
        "similarity_score": 50.0,
        "word_count_difference_ratio": 0.40,
        "sentence_count_difference_ratio": 0.40,
        "character_count_difference_ratio": 0.40,
        "unique_word_difference_ratio": 0.40,
    }

    result = run_v1_v2_comparison(
        features
    )

    assert result["v1"]["risk_level"] == "medium"
    assert result["v2"]["risk_level"] == "medium"

    assert (
        result["v1"]["risk_score"]
        == 50.0
    )


# =====================================================
# CASE 3
# HIGH SIMILARITY + VERY SIMILAR STRUCTURE
# =====================================================

def test_case_3_high_similarity_matching_structure():
    features = {
        "similarity_score": 85.0,
        "word_count_difference_ratio": 0.05,
        "sentence_count_difference_ratio": 0.05,
        "character_count_difference_ratio": 0.05,
        "unique_word_difference_ratio": 0.05,
    }

    result = run_v1_v2_comparison(
        features
    )

    assert result["v1"]["risk_level"] == "critical"
    assert result["v2"]["risk_level"] == "critical"

    assert (
        result["v1"]["risk_score"]
        == 95.0
    )

    assert (
        result["v2"]["risk_score"]
        == 100.0
    )

    assert (
        result["score_difference"]
        == 5.0
    )


# =====================================================
# CASE 4
# HIGH SIMILARITY + DIFFERENT STRUCTURE
# =====================================================

def test_case_4_high_similarity_different_structure():
    features = {
        "similarity_score": 85.0,
        "word_count_difference_ratio": 0.80,
        "sentence_count_difference_ratio": 0.80,
        "character_count_difference_ratio": 0.80,
        "unique_word_difference_ratio": 0.80,
    }

    result = run_v1_v2_comparison(
        features
    )

    assert result["v1"]["risk_level"] == "critical"

    assert (
        result["v1"]["risk_score"]
        == 95.0
    )

    # V2 should be lower because the
    # structural features are very different.
    assert (
        result["v2"]["risk_score"]
        < result["v1"]["risk_score"]
    )


# =====================================================
# CASE 5
# SIMILARITY THRESHOLD COMPARISON
# =====================================================

def test_case_5_similarity_thresholds():
    scenarios = [
        (20.0, "low", 20.0),
        (40.0, "medium", 50.0),
        (60.0, "high", 75.0),
        (80.0, "critical", 95.0),
    ]

    for similarity, expected_level, expected_score in scenarios:

        result = calculate_risk(
            similarity
        )

        assert (
            result["risk_level"]
            == expected_level
        )

        assert (
            result["risk_score"]
            == expected_score
        )


# =====================================================
# CASE 6
# V2 FEATURE CONTRIBUTION
# =====================================================

def test_case_6_v2_feature_contribution():
    features = {
        "similarity_score": 60.0,
        "word_count_difference_ratio": 0.05,
        "sentence_count_difference_ratio": 0.05,
        "character_count_difference_ratio": 0.05,
        "unique_word_difference_ratio": 0.05,
    }

    result = calculate_feature_based_risk(
        features
    )

    # Similarity contribution:
    # 60 -> +45
    #
    # Word count:
    # 0.05 -> +15
    #
    # Sentence count:
    # 0.05 -> +10
    #
    # Character count:
    # 0.05 -> +10
    #
    # Unique words:
    # 0.05 -> +5
    #
    # Total = 85

    assert (
        result["risk_score"]
        == 85.0
    )

    assert (
        result["risk_level"]
        == "critical"
    )

    assert len(
        result["risk_factors"]
    ) >= 5