import csv
import json
from pathlib import Path

import pytest


# =====================================================
# EXPERIMENT 14
# FINAL RESEARCH EVIDENCE CONSOLIDATION
# =====================================================

TESTS_DIR = Path(__file__).resolve().parent

BENCHMARK_FILE = (
    TESTS_DIR
    / "experiment_09_results.csv"
)

MULTI_DOCUMENT_FILE = (
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

REPRODUCIBILITY_FILE = (
    TESTS_DIR
    / "experiment_13_reproducibility_report.json"
)

FINAL_JSON_FILE = (
    TESTS_DIR
    / "experiment_14_final_evidence.json"
)

FINAL_CSV_FILE = (
    TESTS_DIR
    / "experiment_14_evidence_matrix.csv"
)


# =====================================================
# HELPERS
# =====================================================

def load_csv(path):
    assert path.exists()

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def load_json(path):
    assert path.exists()

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# =====================================================
# CASE 1
# EXPERIMENT 09 EVIDENCE
# =====================================================

def test_experiment_09_benchmark_evidence():

    rows = load_csv(
        BENCHMARK_FILE
    )

    assert len(rows) > 0

    assert all(
        "similarity" in row
        for row in rows
    )


# =====================================================
# CASE 2
# EXPERIMENT 11 EVIDENCE
# =====================================================

def test_experiment_11_multi_document_evidence():

    rows = load_csv(
        MULTI_DOCUMENT_FILE
    )

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
# CASE 3
# EXPERIMENT 12 STATISTICS
# =====================================================

def test_experiment_12_statistics_evidence():

    report = load_json(
        STATISTICS_FILE
    )

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

    assert (
        0
        <= report["similarity"]["mean"]
        <= 100
    )

    assert (
        0
        <= report["risk_v1"]["mean"]
        <= 100
    )

    assert (
        0
        <= report["risk_v2"]["mean"]
        <= 100
    )


# =====================================================
# CASE 4
# EXPERIMENT 12 SUMMARY
# =====================================================

def test_experiment_12_summary_evidence():

    rows = load_csv(
        SUMMARY_FILE
    )

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
# CASE 5
# EXPERIMENT 13 EVIDENCE
# =====================================================

def test_experiment_13_reproducibility_evidence():

    report = load_json(
        REPRODUCIBILITY_FILE
    )

    assert (
        report["project"]
        == "EXAMGUARD AI"
    )

    assert (
        report["experiment"]
        == "Experiment 13"
    )

    reproducibility = (
        report["reproducibility"]
    )

    assert (
        reproducibility[
            "text_analysis"
        ]
        is True
    )

    assert (
        reproducibility[
            "similarity"
        ]
        is True
    )

    assert (
        reproducibility[
            "risk_v1"
        ]
        is True
    )

    assert (
        reproducibility[
            "risk_v2"
        ]
        is True
    )

    assert (
        reproducibility[
            "alert"
        ]
        is True
    )

    assert (
        reproducibility[
            "analytics"
        ]
        is True
    )


# =====================================================
# CASE 6
# CORE BENCHMARK CROSS-CHECK
# =====================================================

def test_core_benchmark_cross_check():

    report = load_json(
        REPRODUCIBILITY_FILE
    )

    results = (
        report[
            "validated_results"
        ]
    )

    assert (
        results["similarity"]
        == 43.325
    )

    assert (
        results["risk_v1_score"]
        == 50.0
    )

    assert (
        results["risk_v1_level"]
        == "medium"
    )

    assert (
        results["risk_v2_score"]
        == 46.0
    )

    assert (
        results["risk_v2_level"]
        == "medium"
    )

    assert (
        results["v1_v2_difference"]
        == -4.0
    )

    assert (
        results["alert_type"]
        == "moderate_risk"
    )

    assert (
        results["alert_severity"]
        == "medium"
    )


# =====================================================
# CASE 7
# MULTI-DOCUMENT INTEGRITY
# =====================================================

def test_multi_document_integrity():

    rows = load_csv(
        MULTI_DOCUMENT_FILE
    )

    for row in rows:

        document_id = int(
            row["document_id"]
        )

        compared_id = int(
            row["compared_document_id"]
        )

        assert (
            document_id
            != compared_id
        )

        similarity = float(
            row["similarity"]
        )

        risk_v1 = float(
            row["risk_v1_score"]
        )

        risk_v2 = float(
            row["risk_v2_score"]
        )

        assert (
            0
            <= similarity
            <= 100
        )

        assert (
            0
            <= risk_v1
            <= 100
        )

        assert (
            0
            <= risk_v2
            <= 100
        )


# =====================================================
# CASE 8
# STATISTICAL + REPRODUCIBILITY CONSISTENCY
# =====================================================

def test_statistics_reproducibility_consistency():

    statistics = load_json(
        STATISTICS_FILE
    )

    reproducibility = load_json(
        REPRODUCIBILITY_FILE
    )

    assert (
        reproducibility[
            "validated_results"
        ]["similarity"]
        >= 0
    )

    assert (
        reproducibility[
            "validated_results"
        ]["similarity"]
        <= 100
    )

    assert (
        statistics[
            "dataset"
        ]["number_of_evaluations"]
        == 4
    )


# =====================================================
# CASE 9
# BUILD FINAL EVIDENCE MATRIX
# =====================================================

def test_create_evidence_matrix():

    rows = [
        {
            "experiment": "Experiment 09",
            "area": "Benchmark Reporting",
            "artifact": (
                "experiment_09_results.csv"
            ),
            "status": "PASSED",
        },
        {
            "experiment": "Experiment 10",
            "area": "Final Experimental Report",
            "artifact": (
                "experiment_10_report.json"
            ),
            "status": "PASSED",
        },
        {
            "experiment": "Experiment 11",
            "area": "Multi-Document Evaluation",
            "artifact": (
                "experiment_11_multi_document_results.csv"
            ),
            "status": "PASSED",
        },
        {
            "experiment": "Experiment 12",
            "area": "Statistical Analysis",
            "artifact": (
                "experiment_12_statistics.json"
            ),
            "status": "PASSED",
        },
        {
            "experiment": "Experiment 13",
            "area": "Reproducibility",
            "artifact": (
                "experiment_13_reproducibility_report.json"
            ),
            "status": "PASSED",
        },
    ]

    with open(
        FINAL_CSV_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "experiment",
                "area",
                "artifact",
                "status",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    assert FINAL_CSV_FILE.exists()
    assert FINAL_CSV_FILE.stat().st_size > 0


# =====================================================
# CASE 10
# FINAL EVIDENCE MATRIX VALIDATION
# =====================================================

def test_evidence_matrix_validation():

    test_create_evidence_matrix()

    rows = load_csv(
        FINAL_CSV_FILE
    )

    assert len(rows) == 5

    experiments = {
        row["experiment"]
        for row in rows
    }

    assert experiments == {
        "Experiment 09",
        "Experiment 10",
        "Experiment 11",
        "Experiment 12",
        "Experiment 13",
    }

    assert all(
        row["status"] == "PASSED"
        for row in rows
    )


# =====================================================
# CASE 11
# BUILD FINAL JSON EVIDENCE PACKAGE
# =====================================================

def test_create_final_evidence_package():

    statistics = load_json(
        STATISTICS_FILE
    )

    reproducibility = load_json(
        REPRODUCIBILITY_FILE
    )

    multi_document_rows = load_csv(
        MULTI_DOCUMENT_FILE
    )

    final_report = {

        "project": "EXAMGUARD AI",

        "title": (
            "Final Research Evidence "
            "Consolidation"
        ),

        "experiment": "Experiment 14",

        "status": "PASSED",

        "scope": {
            "benchmark_reporting": True,
            "final_experimental_report": True,
            "multi_document_evaluation": True,
            "statistical_analysis": True,
            "reproducibility": True,
        },

        "evidence_sources": [
            "Experiment 09",
            "Experiment 10",
            "Experiment 11",
            "Experiment 12",
            "Experiment 13",
        ],

        "benchmark": {
            "document_pair": "4 vs 3",
            "similarity": 43.325,
            "risk_v1_score": 50.0,
            "risk_v1_level": "medium",
            "risk_v2_score": 46.0,
            "risk_v2_level": "medium",
            "v1_v2_difference": -4.0,
            "alert_type": "moderate_risk",
            "alert_severity": "medium",
        },

        "multi_document": {
            "evaluations": len(
                multi_document_rows
            ),
            "source": (
                "experiment_11_"
                "multi_document_results.csv"
            ),
        },

        "statistics": {
            "average_similarity": (
                statistics[
                    "similarity"
                ]["mean"]
            ),
            "average_risk_v1": (
                statistics[
                    "risk_v1"
                ]["mean"]
            ),
            "average_risk_v2": (
                statistics[
                    "risk_v2"
                ]["mean"]
            ),
            "average_v1_v2_difference": (
                statistics[
                    "v1_vs_v2"
                ]["mean_difference"]
            ),
        },

        "reproducibility": (
            reproducibility[
                "reproducibility"
            ]
        ),

        "validated_results": (
            reproducibility[
                "validated_results"
            ]
        ),

        "research_conclusion": (
            "Across the evaluated real-document "
            "cases, EXAMGUARD AI demonstrated a "
            "consistent end-to-end processing pipeline "
            "covering document text extraction, NLP "
            "analysis, similarity measurement, Risk V1, "
            "Risk V2, alert generation, analytics, and "
            "repeated evaluation."
        ),

        "research_limitation": (
            "The consolidated evidence represents "
            "descriptive evaluation and reproducibility "
            "of the tested documents. It does not "
            "establish population-level accuracy, "
            "precision, recall, or generalization."
        ),
    }

    with open(
        FINAL_JSON_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_report,
            file,
            indent=4,
        )

    assert FINAL_JSON_FILE.exists()

    assert (
        FINAL_JSON_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 12
# FINAL JSON VALIDATION
# =====================================================

def test_final_evidence_package_validation():

    test_create_final_evidence_package()

    report = load_json(
        FINAL_JSON_FILE
    )

    assert (
        report["project"]
        == "EXAMGUARD AI"
    )

    assert (
        report["experiment"]
        == "Experiment 14"
    )

    assert (
        report["status"]
        == "PASSED"
    )

    assert len(
        report["evidence_sources"]
    ) == 5

    assert (
        report["benchmark"][
            "similarity"
        ]
        == 43.325
    )

    assert (
        report["benchmark"][
            "risk_v1_score"
        ]
        == 50.0
    )

    assert (
        report["benchmark"][
            "risk_v2_score"
        ]
        == 46.0
    )

    assert (
        report["benchmark"][
            "v1_v2_difference"
        ]
        == -4.0
    )

    assert (
        report["benchmark"][
            "alert_severity"
        ]
        == "medium"
    )


# =====================================================
# CASE 13
# ARTIFACT COMPLETENESS
# =====================================================

def test_artifact_completeness():

    required_files = [
        BENCHMARK_FILE,
        MULTI_DOCUMENT_FILE,
        STATISTICS_FILE,
        SUMMARY_FILE,
        REPRODUCIBILITY_FILE,
    ]

    for path in required_files:

        assert path.exists()

        assert (
            path.stat().st_size
            > 0
        )


# =====================================================
# CASE 14
# FINAL RESEARCH CLAIM SAFETY
# =====================================================

def test_final_research_claim_safety():

    report = load_json(
        FINAL_JSON_FILE
    )

    conclusion = (
        report[
            "research_conclusion"
        ]
    )

    limitation = (
        report[
            "research_limitation"
        ]
    )

    assert "accuracy" not in (
        conclusion.lower()
    )

    assert "precision" not in (
        conclusion.lower()
    )

    assert "recall" not in (
        conclusion.lower()
    )

    assert "accuracy" in (
        limitation.lower()
    )

    assert "generalization" in (
        limitation.lower()
    )


# =====================================================
# CASE 15
# FINAL EVIDENCE INTEGRITY
# =====================================================

def test_final_evidence_integrity():

    test_create_evidence_matrix()
    test_create_final_evidence_package()

    assert FINAL_CSV_FILE.exists()
    assert FINAL_JSON_FILE.exists()

    matrix = load_csv(
        FINAL_CSV_FILE
    )

    report = load_json(
        FINAL_JSON_FILE
    )

    assert len(matrix) == 5

    assert (
        report["status"]
        == "PASSED"
    )

    assert (
        report["benchmark"][
            "similarity"
        ]
        == 43.325
    )

    assert (
        report["benchmark"][
            "risk_v1_score"
        ]
        == 50.0
    )

    assert (
        report["benchmark"][
            "risk_v2_score"
        ]
        == 46.0
    )

    assert (
        report["benchmark"][
            "alert_severity"
        ]
        == "medium"
    )