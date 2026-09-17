from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 05
# FULL SYSTEM INTEGRATION TESTING
# =====================================================


# =====================================================
# CASE 1
# COMPLETE PIPELINE
# =====================================================

def test_complete_processing_pipeline():
    """
    Verify the complete EXAMGUARD-AI processing flow.

    Document
        ↓
    Text Extraction
        ↓
    NLP Analysis
        ↓
    Similarity
        ↓
    Risk V1
        ↓
    Risk V2
        ↓
    Alert
    """

    response = client.post(
        "/api/documents/4/process/3"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"

    assert data["document"]["id"] == 4

    assert (
        data["compared_document"]["id"]
        == 3
    )

    # Text extraction
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

    # NLP
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

    # Similarity
    assert (
        data["similarity"]["status"]
        == "completed"
    )

    assert (
        data["similarity"]["method"]
        == "tfidf_cosine"
    )

    assert (
        0 <= float(
            data["similarity"]["score"]
        ) <= 100
    )

    # Risk V1
    assert (
        data["risk_v1"]["model"]
        == "risk-rule-v1"
    )

    assert data["risk_v1"]["level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    # Risk V2
    assert (
        data["risk_v2"]["model"]
        == "risk-rule-v2"
    )

    assert data["risk_v2"]["level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    # Alert
    assert data["alert"]["severity"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert data["alert"]["status"] in {
        "open",
        "resolved",
    }


# =====================================================
# CASE 2
# SELF COMPARISON
# =====================================================

def test_self_comparison_is_rejected():
    """
    A document must never be compared with itself.
    """

    response = client.post(
        "/api/documents/4/process/4"
    )

    assert response.status_code == 400


# =====================================================
# CASE 3
# INVALID DOCUMENT ID
# =====================================================

def test_invalid_document_is_rejected():
    """
    Processing a non-existing document should
    return an appropriate client error.
    """

    response = client.post(
        "/api/documents/999999/process/3"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 4
# INVALID COMPARED DOCUMENT ID
# =====================================================

def test_invalid_compared_document_is_rejected():
    """
    Processing against a non-existing comparison
    document should fail safely.
    """

    response = client.post(
        "/api/documents/4/process/999999"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 5
# DOCUMENT TEXT AVAILABLE
# =====================================================

def test_pipeline_document_text_available():
    """
    The pipeline should leave extracted text
    available for downstream processing.
    """

    response = client.get(
        "/api/documents/4/text"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4

    assert isinstance(
        data["extracted_text"],
        str,
    )

    assert (
        len(
            data["extracted_text"].strip()
        ) > 0
    )


# =====================================================
# CASE 6
# NLP DEPENDENCY
# =====================================================

def test_pipeline_nlp_dependency():
    """
    Verify that NLP analysis exists before
    risk evaluation.
    """

    response = client.get(
        "/api/documents/4/analysis"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["analysis_type"]
        == "nlp_basic"
    )

    result_data = data["result_data"]

    assert (
        int(result_data["word_count"])
        > 0
    )

    assert (
        int(result_data["sentence_count"])
        > 0
    )


# =====================================================
# CASE 7
# SIMILARITY DEPENDENCY
# =====================================================

def test_pipeline_similarity_dependency():
    """
    Verify that document pair has a valid
    similarity result.
    """

    response = client.get(
        "/api/documents/4/similarity/3"
    )

    assert response.status_code == 200

    data = response.json()

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


# =====================================================
# CASE 8
# RISK DEPENDENCY
# =====================================================

def test_pipeline_risk_dependency():
    """
    Verify that both V1 and V2 risk results
    are available after processing.
    """

    v1_response = client.get(
        "/api/documents/4/risk-v1"
    )

    v2_response = client.get(
        "/api/documents/4/risk-v2"
    )

    assert v1_response.status_code == 200

    assert v2_response.status_code == 200

    v1 = v1_response.json()

    v2 = v2_response.json()

    assert (
        v1["model_version"]
        == "risk-rule-v1"
    )

    assert (
        v2["model_version"]
        == "risk-rule-v2"
    )

    assert 0 <= float(
        v1["risk_score"]
    ) <= 100

    assert 0 <= float(
        v2["risk_score"]
    ) <= 100


# =====================================================
# CASE 9
# ALERT DEPENDENCY
# =====================================================

def test_pipeline_alert_dependency():
    """
    Verify that an alert exists after risk
    processing.
    """

    response = client.get(
        "/api/documents/4/alerts"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4

    assert data["risk_score_id"] > 0

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


# =====================================================
# CASE 10
# ANALYTICS INTEGRATION
# =====================================================

def test_pipeline_analytics_integration():
    """
    Verify that processed documents and
    comparisons are reflected in analytics.
    """

    response = client.get(
        "/api/analytics/overview"
    )

    assert response.status_code == 200

    data = response.json()

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

    assert isinstance(
        data["risk_distribution"],
        dict,
    )

    assert isinstance(
        data["alert_distribution"],
        dict,
    )


# =====================================================
# CASE 11
# PIPELINE RESPONSE CONTRACT
# =====================================================

def test_pipeline_response_contract():
    """
    Verify that the full processing endpoint
    returns all required top-level sections.
    """

    response = client.post(
        "/api/documents/4/process/3"
    )

    assert response.status_code == 200

    data = response.json()

    required_sections = {
        "status",
        "document",
        "compared_document",
        "text_extraction",
        "nlp_analysis",
        "similarity",
        "risk_v1",
        "risk_v2",
        "alert",
    }

    assert required_sections.issubset(
        data.keys()
    )


# =====================================================
# CASE 12
# SYSTEM STATUS CONSISTENCY
# =====================================================

def test_system_status_consistency():
    """
    Verify that the root API continues to
    report the system as online.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["project"]
        == "EXAMGUARD AI"
    )

    assert (
        data["status"]
        == "online"
    )

    assert (
        data["version"]
        == "0.1.0"
    )