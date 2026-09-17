import csv
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 11
# MULTI-DOCUMENT / SCALABILITY EVALUATION
# =====================================================

TESTS_DIR = Path(__file__).resolve().parent

REPORT_FILE = (
    TESTS_DIR
    / "experiment_11_multi_document_results.csv"
)


# Existing real documents in EXAMGUARD-AI
DOCUMENT_IDS = [1, 2, 3, 4]


# =====================================================
# HELPER
# =====================================================

def get_json(endpoint):
    response = client.get(endpoint)

    assert response.status_code == 200

    return response.json()


def process_pair(document_id, compared_document_id):
    """
    Run the complete processing pipeline for
    one document pair.
    """

    response = client.post(
        f"/api/documents/"
        f"{document_id}/process/"
        f"{compared_document_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"

    return data


def collect_pair_result(
    document_id,
    compared_document_id,
):
    """
    Process one pair and convert its result into
    a compact benchmark record.
    """

    data = process_pair(
        document_id,
        compared_document_id,
    )

    similarity = float(
        data["similarity"]["score"]
    )

    risk_v1 = float(
        data["risk_v1"]["score"]
    )

    risk_v2 = float(
        data["risk_v2"]["score"]
    )

    return {
        "document_id": document_id,
        "compared_document_id": compared_document_id,
        "similarity": round(
            similarity,
            3,
        ),
        "risk_v1_score": round(
            risk_v1,
            2,
        ),
        "risk_v1_level": (
            data["risk_v1"]["level"]
        ),
        "risk_v2_score": round(
            risk_v2,
            2,
        ),
        "risk_v2_level": (
            data["risk_v2"]["level"]
        ),
        "v1_v2_difference": round(
            risk_v2 - risk_v1,
            2,
        ),
        "alert_severity": (
            data["alert"]["severity"]
        ),
    }


# =====================================================
# CASE 1
# DOCUMENT INVENTORY
# =====================================================

def test_document_inventory():
    """
    Verify that the expected real documents are
    available before multi-document evaluation.
    """

    response = client.get(
        "/api/documents/"
    )

    assert response.status_code == 200

    documents = response.json()

    ids = {
        int(document["id"])
        for document in documents
    }

    for document_id in DOCUMENT_IDS:
        assert document_id in ids


# =====================================================
# CASE 2
# PAIR 1 — DOCUMENT 4 VS 3
# =====================================================

def test_pair_4_vs_3():
    """
    Evaluate the known high-similarity test pair.
    """

    result = collect_pair_result(4, 3)

    assert (
        result["similarity"]
        == 43.325
    )

    assert (
        result["risk_v1_score"]
        == 50.0
    )

    assert (
        result["risk_v2_score"]
        == 46.0
    )

    assert (
        result["risk_v1_level"]
        == "medium"
    )

    assert (
        result["risk_v2_level"]
        == "medium"
    )


# =====================================================
# CASE 3
# PAIR 3 — DOCUMENT 3 VS 4
# =====================================================

def test_pair_3_vs_4():
    """
    Evaluate the reverse document direction.

    This verifies that the endpoint accepts the
    reverse pair and returns valid bounded metrics.
    """

    result = collect_pair_result(3, 4)

    assert (
        result["document_id"]
        == 3
    )

    assert (
        result["compared_document_id"]
        == 4
    )

    assert (
        0 <= result["similarity"] <= 100
    )

    assert (
        0 <= result["risk_v1_score"] <= 100
    )

    assert (
        0 <= result["risk_v2_score"] <= 100
    )


# =====================================================
# CASE 4
# PAIR 1 — DOCUMENT 1 VS 2
# =====================================================

def test_pair_1_vs_2():
    """
    Evaluate another real-document pair.
    """

    result = collect_pair_result(1, 2)

    assert (
        result["document_id"]
        == 1
    )

    assert (
        result["compared_document_id"]
        == 2
    )

    assert (
        0 <= result["similarity"] <= 100
    )

    assert (
        0 <= result["risk_v1_score"] <= 100
    )

    assert (
        0 <= result["risk_v2_score"] <= 100
    )

    assert result["risk_v1_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert result["risk_v2_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }


# =====================================================
# CASE 5
# PAIR 2 — DOCUMENT 2 VS 1
# =====================================================

def test_pair_2_vs_1():
    """
    Evaluate the reverse direction of another
    real-document pair.
    """

    result = collect_pair_result(2, 1)

    assert (
        result["document_id"]
        == 2
    )

    assert (
        result["compared_document_id"]
        == 1
    )

    assert (
        0 <= result["similarity"] <= 100
    )

    assert (
        0 <= result["risk_v1_score"] <= 100
    )

    assert (
        0 <= result["risk_v2_score"] <= 100
    )


# =====================================================
# CASE 6
# MULTI-PAIR BATCH EVALUATION
# =====================================================

def test_multi_pair_batch_evaluation():
    """
    Evaluate multiple real document pairs in one
    controlled batch.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = []

    for document_id, compared_document_id in pairs:

        result = collect_pair_result(
            document_id,
            compared_document_id,
        )

        results.append(result)

    assert len(results) == 4

    for result in results:

        assert (
            result["document_id"]
            != result[
                "compared_document_id"
            ]
        )

        assert (
            0
            <= result["similarity"]
            <= 100
        )

        assert (
            0
            <= result["risk_v1_score"]
            <= 100
        )

        assert (
            0
            <= result["risk_v2_score"]
            <= 100
        )


# =====================================================
# CASE 7
# RISK LEVEL DISTRIBUTION
# =====================================================

def test_multi_pair_risk_distribution():
    """
    Build risk-level distributions across multiple
    real document evaluations.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = [
        collect_pair_result(
            document_id,
            compared_document_id,
        )
        for document_id, compared_document_id
        in pairs
    ]

    v1_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    v2_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for result in results:

        v1_distribution[
            result["risk_v1_level"]
        ] += 1

        v2_distribution[
            result["risk_v2_level"]
        ] += 1

    assert sum(
        v1_distribution.values()
    ) == 4

    assert sum(
        v2_distribution.values()
    ) == 4


# =====================================================
# CASE 8
# AVERAGE METRICS
# =====================================================

def test_multi_pair_average_metrics():
    """
    Calculate aggregate similarity and risk metrics
    over the evaluated document pairs.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = [
        collect_pair_result(
            document_id,
            compared_document_id,
        )
        for document_id, compared_document_id
        in pairs
    ]

    average_similarity = round(
        sum(
            result["similarity"]
            for result in results
        )
        / len(results),
        3,
    )

    average_v1 = round(
        sum(
            result["risk_v1_score"]
            for result in results
        )
        / len(results),
        2,
    )

    average_v2 = round(
        sum(
            result["risk_v2_score"]
            for result in results
        )
        / len(results),
        2,
    )

    assert (
        0
        <= average_similarity
        <= 100
    )

    assert (
        0
        <= average_v1
        <= 100
    )

    assert (
        0
        <= average_v2
        <= 100
    )


# =====================================================
# CASE 9
# V1 VS V2 AGGREGATE COMPARISON
# =====================================================

def test_aggregate_v1_vs_v2():
    """
    Compare Risk V1 and Risk V2 across multiple
    real document pairs.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = [
        collect_pair_result(
            document_id,
            compared_document_id,
        )
        for document_id, compared_document_id
        in pairs
    ]

    differences = [
        result["v1_v2_difference"]
        for result in results
    ]

    assert len(differences) == 4

    for difference in differences:

        assert (
            -100
            <= difference
            <= 100
        )


# =====================================================
# CASE 10
# ALERT DISTRIBUTION
# =====================================================

def test_multi_pair_alert_distribution():
    """
    Validate alert severity across multiple
    document evaluations.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = [
        collect_pair_result(
            document_id,
            compared_document_id,
        )
        for document_id, compared_document_id
        in pairs
    ]

    alert_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for result in results:

        severity = result[
            "alert_severity"
        ]

        assert severity in {
            "low",
            "medium",
            "high",
            "critical",
        }

        alert_distribution[
            severity
        ] += 1

    assert sum(
        alert_distribution.values()
    ) == 4


# =====================================================
# CASE 11
# CSV BENCHMARK REPORT
# =====================================================

def test_create_multi_document_report():
    """
    Create a consolidated multi-document benchmark
    CSV report.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    results = [
        collect_pair_result(
            document_id,
            compared_document_id,
        )
        for document_id, compared_document_id
        in pairs
    ]

    fieldnames = [
        "document_id",
        "compared_document_id",
        "similarity",
        "risk_v1_score",
        "risk_v1_level",
        "risk_v2_score",
        "risk_v2_level",
        "v1_v2_difference",
        "alert_severity",
    ]

    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(results)

    assert REPORT_FILE.exists()

    assert (
        REPORT_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 12
# CSV REPORT VALIDATION
# =====================================================

def test_multi_document_report_content():
    """
    Validate the generated multi-document report.
    """

    test_create_multi_document_report()

    with open(
        REPORT_FILE,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    assert len(rows) == 4

    required_columns = {
        "document_id",
        "compared_document_id",
        "similarity",
        "risk_v1_score",
        "risk_v1_level",
        "risk_v2_score",
        "risk_v2_level",
        "v1_v2_difference",
        "alert_severity",
    }

    assert required_columns.issubset(
        reader.fieldnames
    )

    for row in rows:

        assert (
            int(
                row["document_id"]
            )
            != int(
                row[
                    "compared_document_id"
                ]
            )
        )

        assert (
            0
            <= float(
                row["similarity"]
            )
            <= 100
        )

        assert (
            0
            <= float(
                row["risk_v1_score"]
            )
            <= 100
        )

        assert (
            0
            <= float(
                row["risk_v2_score"]
            )
            <= 100
        )


# =====================================================
# CASE 13
# ANALYTICS AFTER MULTI-DOCUMENT EVALUATION
# =====================================================

def test_analytics_after_multi_document_evaluation():
    """
    Verify that aggregate system analytics remain
    valid after multi-document processing.
    """

    response = client.get(
        "/api/analytics/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["total_documents"]
        >= 4
    )

    assert (
        data["analyzed_documents"]
        >= 4
    )

    assert (
        data["similarity_comparisons"]
        >= 4
    )

    assert (
        0
        <= float(
            data["average_similarity"]
        )
        <= 100
    )

    assert (
        0
        <= float(
            data["processing_rate"]
        )
        <= 100
    )

    assert (
        data["analytics_status"]
        == "active"
    )


# =====================================================
# CASE 14
# FINAL MULTI-DOCUMENT INTEGRITY
# =====================================================

def test_final_multi_document_integrity():
    """
    Final integrity check for the multi-document
    evaluation experiment.
    """

    pairs = [
        (4, 3),
        (3, 4),
        (1, 2),
        (2, 1),
    ]

    for document_id, compared_document_id in pairs:

        result = collect_pair_result(
            document_id,
            compared_document_id,
        )

        assert (
            result["document_id"]
            != result[
                "compared_document_id"
            ]
        )

        assert (
            0
            <= result["similarity"]
            <= 100
        )

        assert (
            0
            <= result["risk_v1_score"]
            <= 100
        )

        assert (
            0
            <= result["risk_v2_score"]
            <= 100
        )

        assert (
            result["risk_v1_level"]
            in {
                "low",
                "medium",
                "high",
                "critical",
            }
        )

        assert (
            result["risk_v2_level"]
            in {
                "low",
                "medium",
                "high",
                "critical",
            }
        )

        assert (
            result["alert_severity"]
            in {
                "low",
                "medium",
                "high",
                "critical",
            }
        )