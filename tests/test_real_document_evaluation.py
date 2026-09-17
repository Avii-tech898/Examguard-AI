from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 03
# REAL DOCUMENT EVALUATION
# =====================================================


def get_json(path):
    """
    Helper for GET requests.
    """
    response = client.get(path)

    assert response.status_code == 200

    return response.json()


# =====================================================
# CASE 1
# REAL DOCUMENT INVENTORY
# =====================================================

def test_real_document_inventory():
    """
    Verify that the real database contains
    the documents used for evaluation.
    """

    documents = get_json(
        "/api/documents/"
    )

    assert isinstance(
        documents,
        list
    )

    assert len(documents) >= 2

    document_ids = {
        int(document["id"])
        for document in documents
    }

    assert 3 in document_ids
    assert 4 in document_ids


# =====================================================
# CASE 2
# REAL DOCUMENT 4 TEXT
# =====================================================

def test_real_document_4_text():
    """
    Verify extracted text for real document 4.
    """

    data = get_json(
        "/api/documents/4/text"
    )

    assert data["document_id"] == 4

    assert (
        isinstance(
            data["extracted_text"],
            str
        )
    )

    assert (
        len(data["extracted_text"].strip())
        > 0
    )


# =====================================================
# CASE 3
# REAL DOCUMENT 4 NLP ANALYSIS
# =====================================================

def test_real_document_4_analysis():
    """
    Verify NLP analysis generated for
    real document 4.
    """

    data = get_json(
        "/api/documents/4/analysis"
    )

    assert data["document_id"] == 4

    assert (
        data["analysis_type"]
        == "nlp_basic"
    )

    result_data = data["result_data"]

    assert isinstance(
        result_data,
        dict
    )

    assert int(
        result_data["word_count"]
    ) > 0

    assert int(
        result_data["sentence_count"]
    ) > 0

    assert int(
        result_data["character_count"]
    ) > 0

    assert int(
        result_data["unique_word_count"]
    ) > 0


# =====================================================
# CASE 4
# REAL DOCUMENT 4 vs 3
# SIMILARITY
# =====================================================

def test_real_document_similarity_4_vs_3():
    """
    Evaluate the actual stored similarity
    between document 4 and document 3.
    """

    data = get_json(
        "/api/documents/4/similarity/3"
    )

    assert data["document_id"] == 4

    assert (
        data["compared_document_id"]
        == 3
    )

    assert (
        0 <= float(
            data["similarity_score"]
        ) <= 100
    )

    assert (
        data["similarity_method"]
        == "tfidf_cosine"
    )

    # Known real evaluation result.
    assert round(
        float(
            data["similarity_score"]
        ),
        3
    ) == 43.325


# =====================================================
# CASE 5
# REAL DOCUMENT 4 RISK V1
# =====================================================

def test_real_document_4_risk_v1():
    """
    Evaluate actual Risk Engine V1
    result stored for document 4.
    """

    data = get_json(
        "/api/documents/4/risk-v1"
    )

    assert data["document_id"] == 4

    assert (
        data["model_version"]
        == "risk-rule-v1"
    )

    score = float(
        data["risk_score"]
    )

    assert 0 <= score <= 100

    assert data["risk_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    # Actual result previously generated
    # from document 4 vs document 3.
    assert score == 50.0

    assert (
        data["risk_level"]
        == "medium"
    )


# =====================================================
# CASE 6
# REAL DOCUMENT 4 RISK V2
# =====================================================

def test_real_document_4_risk_v2():
    """
    Evaluate actual Risk Engine V2
    result stored for document 4.
    """

    data = get_json(
        "/api/documents/4/risk-v2"
    )

    assert data["document_id"] == 4

    assert (
        data["model_version"]
        == "risk-rule-v2"
    )

    score = float(
        data["risk_score"]
    )

    assert 0 <= score <= 100

    assert data["risk_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert isinstance(
        data["risk_factors"],
        list
    )

    # Actual result previously generated
    # from document 4 vs document 3.
    assert score == 46.0

    assert (
        data["risk_level"]
        == "medium"
    )


# =====================================================
# CASE 7
# REAL DOCUMENT ALERT
# =====================================================

def test_real_document_4_alert():
    """
    Verify the alert generated from
    the real V2 risk assessment.
    """

    data = get_json(
        "/api/documents/4/alerts"
    )

    assert data["document_id"] == 4

    assert (
        data["risk_score_id"]
        > 0
    )

    assert data["alert_type"] in {
        "low_risk",
        "moderate_risk",
        "high_risk",
        "critical_risk",
    }

    assert data["severity"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert data["status"] in {
        "open",
        "resolved",
    }

    assert (
        isinstance(
            data["message"],
            str
        )
    )


# =====================================================
# CASE 8
# FULL REAL PIPELINE
# =====================================================

def test_real_document_full_pipeline():
    """
    Execute the complete processing pipeline
    for the real document pair 4 vs 3.

    This verifies:

        extraction
            ↓
        NLP
            ↓
        similarity
            ↓
        Risk V1
            ↓
        Risk V2
            ↓
        alert
    """

    response = client.post(
        "/api/documents/4/process/3"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "completed"
    )

    assert (
        data["document"]["id"]
        == 4
    )

    assert (
        data["compared_document"]["id"]
        == 3
    )

    assert (
        data["text_extraction"]
        ["current_document"]
        == "completed"
    )

    assert (
        data["text_extraction"]
        ["compared_document"]
        == "completed"
    )

    assert (
        data["nlp_analysis"]
        ["current_document"]
        == "completed"
    )

    assert (
        data["nlp_analysis"]
        ["compared_document"]
        == "completed"
    )

    assert (
        data["similarity"]["status"]
        == "completed"
    )

    assert (
        data["similarity"]["method"]
        == "tfidf_cosine"
    )

    assert (
        data["risk_v1"]["model"]
        == "risk-rule-v1"
    )

    assert (
        data["risk_v2"]["model"]
        == "risk-rule-v2"
    )

    assert (
        data["alert"]["status"]
        in {
            "open",
            "resolved",
        }
    )


# =====================================================
# CASE 9
# REAL V1 vs V2 COMPARISON
# =====================================================

def test_real_v1_vs_v2_comparison():
    """
    Compare the actual stored V1 and V2
    results for document 4.
    """

    v1 = get_json(
        "/api/documents/4/risk-v1"
    )

    v2 = get_json(
        "/api/documents/4/risk-v2"
    )

    similarity = get_json(
        "/api/documents/4/similarity/3"
    )

    v1_score = float(
        v1["risk_score"]
    )

    v2_score = float(
        v2["risk_score"]
    )

    similarity_score = float(
        similarity["similarity_score"]
    )

    assert (
        v1["model_version"]
        == "risk-rule-v1"
    )

    assert (
        v2["model_version"]
        == "risk-rule-v2"
    )

    assert (
        0 <= similarity_score <= 100
    )

    assert (
        0 <= v1_score <= 100
    )

    assert (
        0 <= v2_score <= 100
    )

    # Actual observed relationship:
    # V1 = 50
    # V2 = 46
    #
    # Therefore V2 is lower than V1
    # for this real document pair.
    assert v2_score < v1_score


# =====================================================
# CASE 10
# ANALYTICS AFTER REAL EVALUATION
# =====================================================

def test_real_evaluation_analytics():
    """
    Verify that the real document evaluation
    is reflected in system analytics.
    """

    data = get_json(
        "/api/analytics/overview"
    )

    assert (
        int(data["total_documents"])
        >= 4
    )

    assert (
        int(data["analyzed_documents"])
        >= 4
    )

    assert (
        int(data["similarity_comparisons"])
        >= 1
    )

    assert (
        0 <= float(
            data["average_similarity"]
        ) <= 100
    )

    assert (
        0 <= float(
            data["processing_rate"]
        ) <= 100
    )

    assert (
        isinstance(
            data["risk_distribution"],
            dict
        )
    )