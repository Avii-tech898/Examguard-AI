import csv
import json
import math
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

TESTS_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    TESTS_DIR
    / "experiment_11_multi_document_results.csv"
)

STATISTICS_FILE = (
    TESTS_DIR
    / "experiment_12_statistics.json"
)

SUMMARY_FILE = (
    TESTS_DIR
    / "experiment_12_summary.csv"
)


# =====================================================
# HELPERS
# =====================================================

def load_results():
    """
    Load Experiment 11 benchmark results.
    """

    assert INPUT_FILE.exists()

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        rows = list(csv.DictReader(file))

    assert len(rows) >= 4

    return rows


def mean(values):
    return sum(values) / len(values)


def population_std(values):
    avg = mean(values)

    variance = sum(
        (value - avg) ** 2
        for value in values
    ) / len(values)

    return math.sqrt(variance)


def numeric_values(rows, field):
    return [
        float(row[field])
        for row in rows
    ]


# =====================================================
# CASE 1
# DATASET LOAD
# =====================================================

def test_load_experiment_11_dataset():

    rows = load_results()

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
        rows[0].keys()
    )


# =====================================================
# CASE 2
# SIMILARITY STATISTICS
# =====================================================

def test_similarity_statistics():

    rows = load_results()

    values = numeric_values(
        rows,
        "similarity",
    )

    assert all(
        0 <= value <= 100
        for value in values
    )

    average = mean(values)
    minimum = min(values)
    maximum = max(values)
    std = population_std(values)

    assert 0 <= average <= 100
    assert 0 <= minimum <= 100
    assert 0 <= maximum <= 100
    assert std >= 0


# =====================================================
# CASE 3
# RISK V1 STATISTICS
# =====================================================

def test_risk_v1_statistics():

    rows = load_results()

    values = numeric_values(
        rows,
        "risk_v1_score",
    )

    assert all(
        0 <= value <= 100
        for value in values
    )

    average = mean(values)
    minimum = min(values)
    maximum = max(values)

    assert 0 <= average <= 100
    assert 0 <= minimum <= 100
    assert 0 <= maximum <= 100


# =====================================================
# CASE 4
# RISK V2 STATISTICS
# =====================================================

def test_risk_v2_statistics():

    rows = load_results()

    values = numeric_values(
        rows,
        "risk_v2_score",
    )

    assert all(
        0 <= value <= 100
        for value in values
    )

    average = mean(values)
    minimum = min(values)
    maximum = max(values)

    assert 0 <= average <= 100
    assert 0 <= minimum <= 100
    assert 0 <= maximum <= 100


# =====================================================
# CASE 5
# V1 VS V2 DIFFERENCE
# =====================================================

def test_v1_v2_difference_statistics():

    rows = load_results()

    differences = numeric_values(
        rows,
        "v1_v2_difference",
    )

    assert len(differences) == 4

    for difference in differences:

        assert (
            -100
            <= difference
            <= 100
        )

    average_difference = mean(
        differences
    )

    assert (
        -100
        <= average_difference
        <= 100
    )


# =====================================================
# CASE 6
# RISK DISTRIBUTION
# =====================================================

def test_risk_distribution():

    rows = load_results()

    v1_levels = [
        row["risk_v1_level"]
        for row in rows
    ]

    v2_levels = [
        row["risk_v2_level"]
        for row in rows
    ]

    valid_levels = {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert all(
        level in valid_levels
        for level in v1_levels
    )

    assert all(
        level in valid_levels
        for level in v2_levels
    )

    v1_distribution = Counter(
        v1_levels
    )

    v2_distribution = Counter(
        v2_levels
    )

    assert sum(
        v1_distribution.values()
    ) == 4

    assert sum(
        v2_distribution.values()
    ) == 4


# =====================================================
# CASE 7
# ALERT DISTRIBUTION
# =====================================================

def test_alert_distribution():

    rows = load_results()

    alerts = [
        row["alert_severity"]
        for row in rows
    ]

    valid_severity = {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert all(
        severity in valid_severity
        for severity in alerts
    )

    distribution = Counter(
        alerts
    )

    assert sum(
        distribution.values()
    ) == 4


# =====================================================
# CASE 8
# RESEARCH STATISTICS REPORT
# =====================================================

def test_create_statistics_report():

    rows = load_results()

    similarity = numeric_values(
        rows,
        "similarity",
    )

    risk_v1 = numeric_values(
        rows,
        "risk_v1_score",
    )

    risk_v2 = numeric_values(
        rows,
        "risk_v2_score",
    )

    differences = numeric_values(
        rows,
        "v1_v2_difference",
    )

    v1_levels = [
        row["risk_v1_level"]
        for row in rows
    ]

    v2_levels = [
        row["risk_v2_level"]
        for row in rows
    ]

    alerts = [
        row["alert_severity"]
        for row in rows
    ]

    report = {

        "project": "EXAMGUARD AI",

        "experiment": "Experiment 12",

        "title": (
            "Statistical Analysis of "
            "Multi-Document Experimental Results"
        ),

        "dataset": {
            "source": (
                "experiment_11_"
                "multi_document_results.csv"
            ),
            "number_of_evaluations": len(
                rows
            ),
        },

        "similarity": {
            "mean": round(
                mean(similarity),
                3,
            ),
            "minimum": round(
                min(similarity),
                3,
            ),
            "maximum": round(
                max(similarity),
                3,
            ),
            "population_std": round(
                population_std(
                    similarity
                ),
                3,
            ),
        },

        "risk_v1": {
            "mean": round(
                mean(risk_v1),
                2,
            ),
            "minimum": round(
                min(risk_v1),
                2,
            ),
            "maximum": round(
                max(risk_v1),
                2,
            ),
            "population_std": round(
                population_std(risk_v1),
                3,
            ),
        },

        "risk_v2": {
            "mean": round(
                mean(risk_v2),
                2,
            ),
            "minimum": round(
                min(risk_v2),
                2,
            ),
            "maximum": round(
                max(risk_v2),
                2,
            ),
            "population_std": round(
                population_std(risk_v2),
                3,
            ),
        },

        "v1_vs_v2": {
            "mean_difference": round(
                mean(differences),
                2,
            ),
            "minimum_difference": round(
                min(differences),
                2,
            ),
            "maximum_difference": round(
                max(differences),
                2,
            ),
        },

        "risk_distribution": {
            "v1": dict(
                Counter(v1_levels)
            ),
            "v2": dict(
                Counter(v2_levels)
            ),
        },

        "alert_distribution": dict(
            Counter(alerts)
        ),

        "research_notes": [
            (
                "Statistics describe the evaluated "
                "document pairs only."
            ),
            (
                "The results are not a population-level "
                "accuracy estimate."
            ),
            (
                "A larger labeled dataset is required "
                "for formal model accuracy evaluation."
            ),
        ],
    }

    with open(
        STATISTICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )

    assert STATISTICS_FILE.exists()

    assert (
        STATISTICS_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 9
# STATISTICS REPORT VALIDATION
# =====================================================

def test_statistics_report_validation():

    test_create_statistics_report()

    with open(
        STATISTICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(file)

    assert (
        report["project"]
        == "EXAMGUARD AI"
    )

    assert (
        report["experiment"]
        == "Experiment 12"
    )

    assert (
        report["dataset"][
            "number_of_evaluations"
        ]
        == 4
    )

    similarity_mean = (
        report["similarity"]["mean"]
    )

    risk_v1_mean = (
        report["risk_v1"]["mean"]
    )

    risk_v2_mean = (
        report["risk_v2"]["mean"]
    )

    assert (
        0
        <= similarity_mean
        <= 100
    )

    assert (
        0
        <= risk_v1_mean
        <= 100
    )

    assert (
        0
        <= risk_v2_mean
        <= 100
    )


# =====================================================
# CASE 10
# RESEARCH SUMMARY CSV
# =====================================================

def test_create_summary_csv():

    rows = load_results()

    similarity = numeric_values(
        rows,
        "similarity",
    )

    risk_v1 = numeric_values(
        rows,
        "risk_v1_score",
    )

    risk_v2 = numeric_values(
        rows,
        "risk_v2_score",
    )

    differences = numeric_values(
        rows,
        "v1_v2_difference",
    )

    summary = {
        "evaluations": len(rows),
        "average_similarity": round(
            mean(similarity),
            3,
        ),
        "average_risk_v1": round(
            mean(risk_v1),
            2,
        ),
        "average_risk_v2": round(
            mean(risk_v2),
            2,
        ),
        "average_v1_v2_difference": round(
            mean(differences),
            2,
        ),
    }

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(
                summary.keys()
            ),
        )

        writer.writeheader()

        writer.writerow(summary)

    assert SUMMARY_FILE.exists()

    assert (
        SUMMARY_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 11
# SUMMARY CSV VALIDATION
# =====================================================

def test_summary_csv_validation():

    test_create_summary_csv()

    with open(
        SUMMARY_FILE,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    assert len(rows) == 1

    row = rows[0]

    assert (
        int(row["evaluations"])
        == 4
    )

    assert (
        0
        <= float(
            row[
                "average_similarity"
            ]
        )
        <= 100
    )

    assert (
        0
        <= float(
            row[
                "average_risk_v1"
            ]
        )
        <= 100
    )

    assert (
        0
        <= float(
            row[
                "average_risk_v2"
            ]
        )
        <= 100
    )


# =====================================================
# CASE 12
# API ANALYTICS CROSS-CHECK
# =====================================================

def test_api_analytics_cross_check():

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
# CASE 13
# STATISTICAL INTEGRITY
# =====================================================

def test_statistical_integrity():

    rows = load_results()

    similarity = numeric_values(
        rows,
        "similarity",
    )

    risk_v1 = numeric_values(
        rows,
        "risk_v1_score",
    )

    risk_v2 = numeric_values(
        rows,
        "risk_v2_score",
    )

    assert (
        min(similarity)
        <= mean(similarity)
        <= max(similarity)
    )

    assert (
        min(risk_v1)
        <= mean(risk_v1)
        <= max(risk_v1)
    )

    assert (
        min(risk_v2)
        <= mean(risk_v2)
        <= max(risk_v2)
    )


# =====================================================
# CASE 14
# FINAL EXPERIMENT 12 INTEGRITY
# =====================================================

def test_final_experiment_12_integrity():

    test_create_statistics_report()
    test_create_summary_csv()

    assert STATISTICS_FILE.exists()
    assert SUMMARY_FILE.exists()
    assert INPUT_FILE.exists()

    with open(
        STATISTICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(file)

    assert (
        report["dataset"][
            "number_of_evaluations"
        ]
        == 4
    )

    assert (
        len(
            report[
                "research_notes"
            ]
        )
        >= 3
    )