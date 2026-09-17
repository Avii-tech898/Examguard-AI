from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 07
# SECURITY & INPUT VALIDATION TESTING
# =====================================================


# =====================================================
# CASE 1
# NON-EXISTENT DOCUMENT
# =====================================================

def test_nonexistent_document_text():
    """
    Requesting text for a document that does not exist
    should return a controlled 4xx response.
    """

    response = client.get(
        "/api/documents/999999/text"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 2
# NON-EXISTENT DOCUMENT ANALYSIS
# =====================================================

def test_nonexistent_document_analysis():
    """
    Requesting analysis for a missing document
    should not produce an unexpected server error.
    """

    response = client.get(
        "/api/documents/999999/analysis"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 3
# NON-EXISTENT RISK V1
# =====================================================

def test_nonexistent_document_risk_v1():
    """
    Missing document Risk V1 request should fail safely.
    """

    response = client.get(
        "/api/documents/999999/risk-v1"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 4
# NON-EXISTENT RISK V2
# =====================================================

def test_nonexistent_document_risk_v2():
    """
    Missing document Risk V2 request should fail safely.
    """

    response = client.get(
        "/api/documents/999999/risk-v2"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 5
# NON-EXISTENT SIMILARITY PAIR
# =====================================================

def test_nonexistent_similarity_pair():
    """
    Similarity request involving a missing document
    should return a controlled 4xx response.
    """

    response = client.get(
        "/api/documents/4/similarity/999999"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 6
# SELF SIMILARITY
# =====================================================

def test_self_similarity_is_rejected():
    """
    A document should not be compared with itself.
    """

    response = client.get(
        "/api/documents/4/similarity/4"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 7
# SELF PROCESSING
# =====================================================

def test_self_processing_is_rejected():
    """
    A document should not be processed against itself.
    """

    response = client.post(
        "/api/documents/4/process/4"
    )

    assert response.status_code == 400


# =====================================================
# CASE 8
# INVALID PROCESSING DOCUMENT
# =====================================================

def test_invalid_processing_document():
    """
    Processing with a non-existent current document
    should return a controlled 4xx response.
    """

    response = client.post(
        "/api/documents/999999/process/3"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 9
# INVALID COMPARISON DOCUMENT
# =====================================================

def test_invalid_processing_comparison_document():
    """
    Processing with a non-existent comparison document
    should return a controlled 4xx response.
    """

    response = client.post(
        "/api/documents/4/process/999999"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 10
# NEGATIVE DOCUMENT ID
# =====================================================

def test_negative_document_id():
    """
    Negative IDs should not result in an unexpected
    server error.
    """

    endpoints = [
        "/api/documents/-1/text",
        "/api/documents/-1/analysis",
        "/api/documents/-1/risk-v1",
        "/api/documents/-1/risk-v2",
    ]

    for endpoint in endpoints:

        response = client.get(endpoint)

        assert response.status_code < 500


# =====================================================
# CASE 11
# ZERO DOCUMENT ID
# =====================================================

def test_zero_document_id():
    """
    Zero is not a valid existing document ID.
    """

    response = client.get(
        "/api/documents/0/text"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 12
# INVALID SIMILARITY ZERO ID
# =====================================================

def test_zero_similarity_document_id():
    """
    Invalid comparison ID should be handled safely.
    """

    response = client.get(
        "/api/documents/4/similarity/0"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 13
# INVALID PROCESSING ID
# =====================================================

def test_zero_processing_comparison_id():
    """
    Invalid processing comparison ID should not
    cause a 5xx server failure.
    """

    response = client.post(
        "/api/documents/4/process/0"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 14
# API ROUTE CONSISTENCY
# =====================================================

def test_unknown_api_route():
    """
    Unknown API routes should return 404 rather than
    an unexpected server error.
    """

    response = client.get(
        "/api/this-route-does-not-exist"
    )

    assert response.status_code == 404


# =====================================================
# CASE 15
# UNKNOWN HTTP METHOD
# =====================================================

def test_invalid_http_method():
    """
    Unsupported HTTP methods should return a controlled
    4xx response.
    """

    response = client.delete(
        "/api/documents/"
    )

    assert response.status_code in {
        405,
        404,
    }


# =====================================================
# CASE 16
# MALFORMED PATH
# =====================================================

def test_malformed_document_path():
    """
    Malformed document paths should not create
    unexpected 5xx responses.
    """

    endpoints = [
        "/api/documents/not-a-number/text",
        "/api/documents/abc/analysis",
        "/api/documents/xyz/risk-v1",
        "/api/documents/test/risk-v2",
    ]

    for endpoint in endpoints:

        response = client.get(endpoint)

        assert response.status_code < 500


# =====================================================
# CASE 17
# ALERT FOR NON-EXISTENT DOCUMENT
# =====================================================

def test_nonexistent_document_alert():
    """
    Alert retrieval for a missing document should
    return a controlled response.
    """

    response = client.get(
        "/api/documents/999999/alerts"
    )

    assert response.status_code in {
        400,
        404,
    }


# =====================================================
# CASE 18
# SECURITY REGRESSION CHECK
# =====================================================

def test_security_regression_check():
    """
    Basic security regression check:
    known valid endpoints must continue working
    after invalid requests.
    """

    endpoints = [
        "/",
        "/api/v1/health",
        "/api/documents/",
        "/api/analytics/overview",
        "/api/documents/4/text",
        "/api/documents/4/analysis",
        "/api/documents/4/risk-v1",
        "/api/documents/4/risk-v2",
        "/api/documents/4/similarity/3",
        "/api/documents/4/alerts",
    ]

    for endpoint in endpoints:

        response = client.get(endpoint)

        assert (
            200
            <= response.status_code
            < 300
        )