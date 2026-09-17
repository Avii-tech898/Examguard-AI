from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# ROOT API
# =====================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "EXAMGUARD AI"
    assert data["status"] == "online"
    assert data["version"] == "0.1.0"


# =====================================================
# HEALTH API
# =====================================================

def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "EXAMGUARD AI Backend"
    assert data["version"] == "v1"


# =====================================================
# DOCUMENTS API
# =====================================================

def test_get_documents():
    response = client.get("/api/documents/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# =====================================================
# ANALYTICS API
# =====================================================

def test_analytics_overview():
    response = client.get(
        "/api/analytics/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_documents" in data
    assert "analyzed_documents" in data
    assert "similarity_comparisons" in data
    assert "average_similarity" in data
    assert "risk_distribution" in data
    assert "open_alerts" in data
    assert "processing_rate" in data


# =====================================================
# DOCUMENT TEXT API
# =====================================================

def test_document_text():
    response = client.get(
        "/api/documents/4/text"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert "extracted_text" in data


# =====================================================
# NLP ANALYSIS API
# =====================================================

def test_document_analysis():
    response = client.get(
        "/api/documents/4/analysis"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert data["analysis_type"] == "nlp_basic"
    assert "result_data" in data


# =====================================================
# RISK V1 API
# =====================================================

def test_document_risk_v1():
    response = client.get(
        "/api/documents/4/risk-v1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert data["model_version"] == "risk-rule-v1"

    assert 0 <= float(
        data["risk_score"]
    ) <= 100


# =====================================================
# RISK V2 API
# =====================================================

def test_document_risk_v2():
    response = client.get(
        "/api/documents/4/risk-v2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert data["model_version"] == "risk-rule-v2"

    assert 0 <= float(
        data["risk_score"]
    ) <= 100


# =====================================================
# SIMILARITY API
# =====================================================

def test_document_similarity():
    response = client.get(
        "/api/documents/4/similarity/3"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert data["compared_document_id"] == 3

    assert 0 <= float(
        data["similarity_score"]
    ) <= 100


# =====================================================
# ALERT API
# =====================================================

def test_document_alert():
    response = client.get(
        "/api/documents/4/alerts"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 4
    assert "alert_type" in data
    assert "severity" in data
    assert "status" in data