import time

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 06
# PERFORMANCE & RELIABILITY TESTING
# =====================================================


DOCUMENT_ID = 4
COMPARED_DOCUMENT_ID = 3


# =====================================================
# HELPER
# =====================================================

def process_document_pair():
    """
    Execute the real EXAMGUARD-AI processing pipeline
    and measure its response time.
    """

    start_time = time.perf_counter()

    response = client.post(
        f"/api/documents/"
        f"{DOCUMENT_ID}/process/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    elapsed_time = (
        time.perf_counter()
        - start_time
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"

    return data, elapsed_time


# =====================================================
# CASE 1
# SINGLE RUN PERFORMANCE
# =====================================================

def test_single_pipeline_performance():
    """
    Verify that a complete real-document pipeline
    finishes successfully and returns a measurable
    response time.
    """

    data, elapsed_time = (
        process_document_pair()
    )

    assert elapsed_time > 0

    assert elapsed_time < 60

    assert (
        data["similarity"]["status"]
        == "completed"
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
# CASE 2
# SIMILARITY CONSISTENCY
# =====================================================

def test_similarity_consistency():
    """
    Repeated similarity calculations for the same
    document pair should return the same score.
    """

    scores = []

    for _ in range(3):

        response = client.get(
            f"/api/documents/"
            f"{DOCUMENT_ID}/similarity/"
            f"{COMPARED_DOCUMENT_ID}"
        )

        assert response.status_code == 200

        data = response.json()

        scores.append(
            round(
                float(
                    data["similarity_score"]
                ),
                3,
            )
        )

    assert len(scores) == 3

    assert scores[0] == scores[1]
    assert scores[1] == scores[2]


# =====================================================
# CASE 3
# NLP CONSISTENCY
# =====================================================

def test_nlp_consistency():
    """
    Repeated NLP retrieval should return the same
    latest analysis values.
    """

    results = []

    for _ in range(3):

        response = client.get(
            f"/api/documents/"
            f"{DOCUMENT_ID}/analysis"
        )

        assert response.status_code == 200

        data = response.json()

        result_data = data["result_data"]

        results.append(
            (
                int(
                    result_data["word_count"]
                ),
                int(
                    result_data["sentence_count"]
                ),
                int(
                    result_data["character_count"]
                ),
                int(
                    result_data["unique_word_count"]
                ),
            )
        )

    assert results[0] == results[1]
    assert results[1] == results[2]


# =====================================================
# CASE 4
# RISK V1 CONSISTENCY
# =====================================================

def test_risk_v1_consistency():
    """
    Repeated Risk V1 retrieval should return
    the same risk score and level.
    """

    results = []

    for _ in range(3):

        response = client.get(
            f"/api/documents/"
            f"{DOCUMENT_ID}/risk-v1"
        )

        assert response.status_code == 200

        data = response.json()

        results.append(
            (
                float(
                    data["risk_score"]
                ),
                data["risk_level"],
                data["model_version"],
            )
        )

    assert results[0] == results[1]
    assert results[1] == results[2]

    assert (
        results[0][2]
        == "risk-rule-v1"
    )


# =====================================================
# CASE 5
# RISK V2 CONSISTENCY
# =====================================================

def test_risk_v2_consistency():
    """
    Repeated Risk V2 retrieval should return
    the same risk score and level.
    """

    results = []

    for _ in range(3):

        response = client.get(
            f"/api/documents/"
            f"{DOCUMENT_ID}/risk-v2"
        )

        assert response.status_code == 200

        data = response.json()

        results.append(
            (
                float(
                    data["risk_score"]
                ),
                data["risk_level"],
                data["model_version"],
            )
        )

    assert results[0] == results[1]
    assert results[1] == results[2]

    assert (
        results[0][2]
        == "risk-rule-v2"
    )


# =====================================================
# CASE 6
# FULL PIPELINE REPEATABILITY
# =====================================================

def test_full_pipeline_repeatability():
    """
    Execute the complete pipeline three times.

    Core analytical outputs should remain consistent.
    """

    results = []

    for _ in range(3):

        data, elapsed_time = (
            process_document_pair()
        )

        assert elapsed_time < 60

        similarity = round(
            float(
                data["similarity"]["score"]
            ),
            3,
        )

        v1_score = float(
            data["risk_v1"]["score"]
        )

        v2_score = float(
            data["risk_v2"]["score"]
        )

        results.append(
            (
                similarity,
                v1_score,
                v2_score,
                data["risk_v1"]["level"],
                data["risk_v2"]["level"],
            )
        )

    assert results[0] == results[1]
    assert results[1] == results[2]


# =====================================================
# CASE 7
# MULTIPLE API REQUEST RELIABILITY
# =====================================================

def test_multiple_api_requests():
    """
    Execute several read-only API requests
    sequentially and ensure no request fails.
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

        response = client.get(
            endpoint
        )

        assert (
            200
            <= response.status_code
            < 300
        )


# =====================================================
# CASE 8
# ANALYTICS STABILITY
# =====================================================

def test_analytics_stability():
    """
    Repeated analytics requests should remain
    available and return valid metric ranges.
    """

    results = []

    for _ in range(3):

        response = client.get(
            "/api/analytics/overview"
        )

        assert response.status_code == 200

        data = response.json()

        results.append(
            (
                int(
                    data["total_documents"]
                ),
                int(
                    data["analyzed_documents"]
                ),
                int(
                    data["similarity_comparisons"]
                ),
                round(
                    float(
                        data[
                            "average_similarity"
                        ]
                    ),
                    2,
                ),
                round(
                    float(
                        data[
                            "processing_rate"
                        ]
                    ),
                    2,
                ),
            )
        )

    assert results[0] == results[1]
    assert results[1] == results[2]


# =====================================================
# CASE 9
# ERROR HANDLING RELIABILITY
# =====================================================

def test_error_handling_reliability():
    """
    Invalid requests should fail with controlled
    4xx responses instead of unexpected 5xx errors.
    """

    self_comparison = client.post(
        "/api/documents/4/process/4"
    )

    assert (
        self_comparison.status_code
        == 400
    )

    invalid_document = client.post(
        "/api/documents/999999/process/3"
    )

    assert (
        invalid_document.status_code
        in {
            400,
            404,
        }
    )

    invalid_comparison = client.post(
        "/api/documents/4/process/999999"
    )

    assert (
        invalid_comparison.status_code
        in {
            400,
            404,
        }
    )


# =====================================================
# CASE 10
# RESPONSE TIME SANITY
# =====================================================

def test_read_api_response_time():
    """
    Read-only API endpoints should respond within
    a reasonable local-development threshold.
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

        start_time = time.perf_counter()

        response = client.get(
            endpoint
        )

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        assert (
            200
            <= response.status_code
            < 300
        )

        assert elapsed_time < 10