from backend.services.similarity_engine import calculate_similarity
from backend.services.risk_engine import (
    calculate_risk,
    calculate_feature_based_risk,
)
from backend.services.feature_engine import (
    build_document_features,
)


# =====================================================
# EXPERIMENT 01
# SIMILARITY + RISK ENGINE EVALUATION
# =====================================================


def test_low_similarity_case():
    """
    Test Case 1:
    Completely different documents should
    produce low similarity.
    """

    text_a = """
    Python programming and data analysis
    using pandas numpy and machine learning.
    """

    text_b = """
    The examination schedule contains
    mathematics physics and chemistry subjects.
    """

    similarity = calculate_similarity(
        text_a,
        text_b,
    )

    risk = calculate_risk(
        similarity
    )

    assert similarity < 30
    assert risk["risk_level"] == "low"


def test_identical_documents():
    """
    Test Case 2:
    Identical documents should produce
    approximately 100% similarity.
    """

    text = """
    EXAMGUARD AI examination security
    detects suspicious document similarity.
    """

    similarity = calculate_similarity(
        text,
        text,
    )

    assert similarity >= 99


def test_high_similarity_risk():
    """
    Test Case 3:
    Very high similarity should produce
    critical V1 risk.
    """

    text_a = """
    Python SQL Power BI Excel data analysis
    machine learning artificial intelligence.
    """

    text_b = """
    Python SQL Power BI Excel data analysis
    machine learning artificial intelligence.
    """

    similarity = calculate_similarity(
        text_a,
        text_b,
    )

    risk = calculate_risk(
        similarity
    )

    assert similarity >= 80
    assert risk["risk_level"] == "critical"
    assert risk["risk_score"] == 95.0


def test_feature_based_risk():
    """
    Test Case 4:
    Similarity + similar document structure
    should increase V2 risk.
    """

    features = {
        "similarity_score": 85.0,

        "word_count_difference_ratio": 0.05,

        "sentence_count_difference_ratio": 0.05,

        "character_count_difference_ratio": 0.05,

        "unique_word_difference_ratio": 0.05,
    }

    risk = calculate_feature_based_risk(
        features
    )

    assert risk["risk_score"] > 80
    assert risk["risk_level"] == "critical"


def test_feature_difference_reduces_risk():
    """
    Test Case 5:
    High similarity with large structural
    differences should produce a lower
    V2 score than highly matching structure.
    """

    similar_features = {
        "similarity_score": 85.0,
        "word_count_difference_ratio": 0.05,
        "sentence_count_difference_ratio": 0.05,
        "character_count_difference_ratio": 0.05,
        "unique_word_difference_ratio": 0.05,
    }

    different_features = {
        "similarity_score": 85.0,
        "word_count_difference_ratio": 0.80,
        "sentence_count_difference_ratio": 0.80,
        "character_count_difference_ratio": 0.80,
        "unique_word_difference_ratio": 0.80,
    }

    similar_risk = calculate_feature_based_risk(
        similar_features
    )

    different_risk = calculate_feature_based_risk(
        different_features
    )

    assert (
        similar_risk["risk_score"]
        > different_risk["risk_score"]
    )


def test_document_feature_generation():
    """
    Test Case 6:
    Feature engine should correctly generate
    normalized document comparison features.
    """

    current_analysis = {
        "result_data": {
            "word_count": 100,
            "sentence_count": 10,
            "character_count": 600,
            "unique_word_count": 70,
        }
    }

    compared_analysis = {
        "result_data": {
            "word_count": 100,
            "sentence_count": 10,
            "character_count": 600,
            "unique_word_count": 70,
        }
    }

    features = build_document_features(
        current_analysis=current_analysis,
        compared_analysis=compared_analysis,
        similarity_score=100.0,
    )

    assert features["similarity_score"] == 100.0

    assert (
        features["word_count_difference_ratio"]
        == 0.0
    )

    assert (
        features["sentence_count_difference_ratio"]
        == 0.0
    )

    assert (
        features["character_count_difference_ratio"]
        == 0.0
    )

    assert (
        features["unique_word_difference_ratio"]
        == 0.0
    )