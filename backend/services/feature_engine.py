from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_difference_ratio(
    value_a: float,
    value_b: float
) -> float:
    """
    Calculate normalized absolute difference between
    two numeric values.
    """
    value_a = safe_float(value_a)
    value_b = safe_float(value_b)

    denominator = max(
        abs(value_a),
        abs(value_b),
        1.0
    )

    return abs(value_a - value_b) / denominator


def build_document_features(
    current_analysis: dict[str, Any] | None,
    compared_analysis: dict[str, Any] | None,
    similarity_score: float | None,
) -> dict[str, Any]:
    """
    Build a feature vector from document NLP analysis
    and document similarity.

    These features are intended for:
    1. Rule-based risk analysis
    2. Future ML model training
    """

    current_analysis = (
        current_analysis
        if isinstance(current_analysis, dict)
        else {}
    )

    compared_analysis = (
        compared_analysis
        if isinstance(compared_analysis, dict)
        else {}
    )

    current_result = current_analysis.get(
        "result_data",
        {}
    )

    compared_result = compared_analysis.get(
        "result_data",
        {}
    )

    if not isinstance(current_result, dict):
        current_result = {}

    if not isinstance(compared_result, dict):
        compared_result = {}


    # =====================================================
    # BASIC NLP FEATURES
    # =====================================================

    current_word_count = safe_float(
        current_result.get("word_count")
    )

    compared_word_count = safe_float(
        compared_result.get("word_count")
    )

    current_sentence_count = safe_float(
        current_result.get("sentence_count")
    )

    compared_sentence_count = safe_float(
        compared_result.get("sentence_count")
    )

    current_character_count = safe_float(
        current_result.get("character_count")
    )

    compared_character_count = safe_float(
        compared_result.get("character_count")
    )

    current_unique_words = safe_float(
        current_result.get("unique_word_count")
    )

    compared_unique_words = safe_float(
        compared_result.get("unique_word_count")
    )


    # =====================================================
    # NORMALIZED FEATURES
    # =====================================================

    word_count_difference = abs(
        current_word_count -
        compared_word_count
    )

    sentence_count_difference = abs(
        current_sentence_count -
        compared_sentence_count
    )

    character_count_difference = abs(
        current_character_count -
        compared_character_count
    )

    unique_word_difference = abs(
        current_unique_words -
        compared_unique_words
    )


    word_count_difference_ratio = (
        calculate_difference_ratio(
            current_word_count,
            compared_word_count
        )
    )

    sentence_count_difference_ratio = (
        calculate_difference_ratio(
            current_sentence_count,
            compared_sentence_count
        )
    )

    character_count_difference_ratio = (
        calculate_difference_ratio(
            current_character_count,
            compared_character_count
        )
    )

    unique_word_difference_ratio = (
        calculate_difference_ratio(
            current_unique_words,
            compared_unique_words
        )
    )


    # =====================================================
    # SIMILARITY FEATURE
    # =====================================================

    similarity_score = safe_float(
        similarity_score
    )

    similarity_ratio = (
        similarity_score / 100.0
    )


    # =====================================================
    # TEXT DENSITY FEATURES
    # =====================================================

    current_words_per_sentence = (
        current_word_count /
        max(current_sentence_count, 1.0)
    )

    compared_words_per_sentence = (
        compared_word_count /
        max(compared_sentence_count, 1.0)
    )

    words_per_sentence_difference = abs(
        current_words_per_sentence -
        compared_words_per_sentence
    )


    # =====================================================
    # FEATURE VECTOR
    # =====================================================

    features = {
        "similarity_score": round(
            similarity_score,
            3
        ),

        "similarity_ratio": round(
            similarity_ratio,
            5
        ),

        "current_word_count": int(
            current_word_count
        ),

        "compared_word_count": int(
            compared_word_count
        ),

        "word_count_difference": int(
            word_count_difference
        ),

        "word_count_difference_ratio": round(
            word_count_difference_ratio,
            5
        ),

        "current_sentence_count": int(
            current_sentence_count
        ),

        "compared_sentence_count": int(
            compared_sentence_count
        ),

        "sentence_count_difference": int(
            sentence_count_difference
        ),

        "sentence_count_difference_ratio": round(
            sentence_count_difference_ratio,
            5
        ),

        "current_character_count": int(
            current_character_count
        ),

        "compared_character_count": int(
            compared_character_count
        ),

        "character_count_difference": int(
            character_count_difference
        ),

        "character_count_difference_ratio": round(
            character_count_difference_ratio,
            5
        ),

        "current_unique_words": int(
            current_unique_words
        ),

        "compared_unique_words": int(
            compared_unique_words
        ),

        "unique_word_difference": int(
            unique_word_difference
        ),

        "unique_word_difference_ratio": round(
            unique_word_difference_ratio,
            5
        ),

        "current_words_per_sentence": round(
            current_words_per_sentence,
            3
        ),

        "compared_words_per_sentence": round(
            compared_words_per_sentence,
            3
        ),

        "words_per_sentence_difference": round(
            words_per_sentence_difference,
            3
        ),
    }

    return features