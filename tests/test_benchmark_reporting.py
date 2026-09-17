import csv
import time
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 09
# DATASET / SCENARIO BENCHMARK
# & RESULT REPORTING
# =====================================================


DOCUMENT_ID = 4
COMPARED_DOCUMENT_ID = 3


REPORT_PATH = (
    Path(__file__).resolve().parent
    / "experiment_09_results.csv"
)


# =====================================================
# HELPER
# =====================================================

def get_json(endpoint):
    """
    Execute GET request and return JSON.
    """

    response = client.get(endpoint)

    assert response.status_code == 200

    return response.json()


def run_real_pipeline():
    """
    Run the complete real-document pipeline
    and collect measurable results.
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

    similarity = float(
        data["similarity"]["score"]
    )

    v1_score = float(
        data["risk_v1"]["score"]
    )

    v2_score = float(
        data["risk_v2"]["score"]
    )

    v1_level = data["risk_v1"]["level"]

    v2_level = data["risk_v2"]["level"]

    alert_severity = data["alert"]["severity"]

    return {
        "scenario": "Real Document 4 vs 3",
        "document_id": DOCUMENT_ID,
        "compared_document_id": COMPARED_DOCUMENT_ID,
        "similarity": round(
            similarity,
            3,
        ),
        "risk_v1_score": round(
            v1_score,
            2,
        ),
        "risk_v1_level": v1_level,
        "risk_v2_score": round(
            v2_score,
            2,
        ),
        "risk_v2_level": v2_level,
        "v1_v2_difference": round(
            v2_score - v1_score,
            2,
        ),
        "alert_severity": alert_severity,
        "processing_time_seconds": round(
            elapsed_time,
            4,
        ),
    }


# =====================================================
# CASE 1
# REAL BENCHMARK GENERATION
# =====================================================

def test_generate_real_benchmark():
    """
    Generate one complete benchmark result from
    the real EXAMGUARD-AI document pipeline.
    """

    result = run_real_pipeline()

    assert (
        result["scenario"]
        == "Real Document 4 vs 3"
    )

    assert (
        result["document_id"]
        == 4
    )

    assert (
        result["compared_document_id"]
        == 3
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

    assert result["alert_severity"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert (
        result["processing_time_seconds"]
        > 0
    )


# =====================================================
# CASE 2
# BENCHMARK NUMERIC CONSISTENCY
# =====================================================

def test_benchmark_numeric_consistency():
    """
    Verify that repeated benchmark runs produce
    stable analytical values.
    """

    first = run_real_pipeline()
    second = run_real_pipeline()

    assert (
        first["similarity"]
        == second["similarity"]
    )

    assert (
        first["risk_v1_score"]
        == second["risk_v1_score"]
    )

    assert (
        first["risk_v2_score"]
        == second["risk_v2_score"]
    )

    assert (
        first["risk_v1_level"]
        == second["risk_v1_level"]
    )

    assert (
        first["risk_v2_level"]
        == second["risk_v2_level"]
    )


# =====================================================
# CASE 3
# V1 VS V2 DELTA
# =====================================================

def test_v1_v2_delta():
    """
    Measure the difference between Risk V1 and V2.
    """

    result = run_real_pipeline()

    expected_delta = round(
        result["risk_v2_score"]
        - result["risk_v1_score"],
        2,
    )

    assert (
        result["v1_v2_difference"]
        == expected_delta
    )


# =====================================================
# CASE 4
# REAL DOCUMENT RESULT VALIDATION
# =====================================================

def test_real_document_expected_result():
    """
    Validate the known real-document benchmark
    generated from document 4 vs document 3.
    """

    result = run_real_pipeline()

    assert (
        result["similarity"]
        == 43.325
    )

    assert (
        result["risk_v1_score"]
        == 50.0
    )

    assert (
        result["risk_v1_level"]
        == "medium"
    )

    assert (
        result["risk_v2_score"]
        == 46.0
    )

    assert (
        result["risk_v2_level"]
        == "medium"
    )

    assert (
        result["v1_v2_difference"]
        == -4.0
    )


# =====================================================
# CASE 5
# ALERT RESULT VALIDATION
# =====================================================

def test_benchmark_alert_result():
    """
    Verify that the benchmark pipeline produces
    an alert consistent with the current risk state.
    """

    result = run_real_pipeline()

    alert = get_json(
        "/api/documents/4/alerts"
    )

    assert alert["document_id"] == 4

    assert alert["severity"] == (
        result["alert_severity"]
    )

    assert alert["status"] in {
        "open",
        "resolved",
    }


# =====================================================
# CASE 6
# BENCHMARK CSV REPORT
# =====================================================

def test_create_benchmark_csv_report():
    """
    Generate a CSV research-style benchmark report.
    """

    results = []

    for _ in range(3):

        result = run_real_pipeline()

        results.append(result)

    fieldnames = [
        "scenario",
        "document_id",
        "compared_document_id",
        "similarity",
        "risk_v1_score",
        "risk_v1_level",
        "risk_v2_score",
        "risk_v2_level",
        "v1_v2_difference",
        "alert_severity",
        "processing_time_seconds",
    ]

    with open(
        REPORT_PATH,
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

    assert REPORT_PATH.exists()

    assert REPORT_PATH.stat().st_size > 0


# =====================================================
# CASE 7
# CSV REPORT CONTENT VALIDATION
# =====================================================

def test_benchmark_csv_content():
    """
    Validate the generated CSV report.
    """

    # Ensure report exists.
    test_create_benchmark_csv_report()

    with open(
        REPORT_PATH,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    assert len(rows) == 3

    required_columns = {
        "scenario",
        "document_id",
        "compared_document_id",
        "similarity",
        "risk_v1_score",
        "risk_v1_level",
        "risk_v2_score",
        "risk_v2_level",
        "v1_v2_difference",
        "alert_severity",
        "processing_time_seconds",
    }

    assert required_columns.issubset(
        reader.fieldnames
    )

    for row in rows:

        assert (
            row["scenario"]
            == "Real Document 4 vs 3"
        )

        assert (
            float(row["similarity"])
            == 43.325
        )

        assert (
            float(row["risk_v1_score"])
            == 50.0
        )

        assert (
            float(row["risk_v2_score"])
            == 46.0
        )

        assert (
            float(
                row["v1_v2_difference"]
            )
            == -4.0
        )


# =====================================================
# CASE 8
# BENCHMARK SUMMARY
# =====================================================

def test_benchmark_summary():
    """
    Calculate a simple benchmark summary from
    repeated real pipeline executions.
    """

    results = [
        run_real_pipeline()
        for _ in range(3)
    ]

    similarities = [
        item["similarity"]
        for item in results
    ]

    v1_scores = [
        item["risk_v1_score"]
        for item in results
    ]

    v2_scores = [
        item["risk_v2_score"]
        for item in results
    ]

    processing_times = [
        item["processing_time_seconds"]
        for item in results
    ]

    average_similarity = round(
        sum(similarities)
        / len(similarities),
        3,
    )

    average_v1 = round(
        sum(v1_scores)
        / len(v1_scores),
        2,
    )

    average_v2 = round(
        sum(v2_scores)
        / len(v2_scores),
        2,
    )

    average_processing_time = round(
        sum(processing_times)
        / len(processing_times),
        4,
    )

    assert (
        average_similarity
        == 43.325
    )

    assert (
        average_v1
        == 50.0
    )

    assert (
        average_v2
        == 46.0
    )

    assert (
        average_processing_time
        > 0
    )


# =====================================================
# CASE 9
# BENCHMARK RANGE VALIDATION
# =====================================================

def test_benchmark_ranges():
    """
    Ensure all benchmark metrics remain inside
    valid operational ranges.
    """

    result = run_real_pipeline()

    assert (
        0 <= result["similarity"] <= 100
    )

    assert (
        0 <= result["risk_v1_score"] <= 100
    )

    assert (
        0 <= result["risk_v2_score"] <= 100
    )

    assert (
        -100
        <= result["v1_v2_difference"]
        <= 100
    )

    assert (
        result["processing_time_seconds"]
        < 60
    )


# =====================================================
# CASE 10
# FINAL BENCHMARK INTEGRITY
# =====================================================

def test_final_benchmark_integrity():
    """
    Final integrity check ensuring the benchmark
    represents one coherent real-document evaluation.
    """

    result = run_real_pipeline()

    assert (
        result["document_id"]
        != result["compared_document_id"]
    )

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
        == result["risk_v2_level"]
        == "medium"
    )

    assert (
        result["v1_v2_difference"]
        == -4.0
    )