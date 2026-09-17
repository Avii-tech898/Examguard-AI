import csv
import json
from pathlib import Path


# =====================================================
# EXPERIMENT 15
# FINAL RESEARCH PACKAGE
# & PUBLICATION READINESS VALIDATION
# =====================================================

TESTS_DIR = Path(__file__).resolve().parent

BENCHMARK_FILE = (
    TESTS_DIR / "experiment_09_results.csv"
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

FINAL_EVIDENCE_FILE = (
    TESTS_DIR
    / "experiment_14_final_evidence.json"
)

EVIDENCE_MATRIX_FILE = (
    TESTS_DIR
    / "experiment_14_evidence_matrix.csv"
)

FINAL_PACKAGE_FILE = (
    TESTS_DIR
    / "experiment_15_final_research_package.json"
)

FINAL_MATRIX_FILE = (
    TESTS_DIR
    / "experiment_15_publication_readiness.csv"
)


# =====================================================
# HELPERS
# =====================================================

def load_json(path):
    assert path.exists(), (
        f"Required JSON artifact missing: {path}"
    )

    assert path.stat().st_size > 0, (
        f"JSON artifact is empty: {path}"
    )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_csv(path):
    assert path.exists(), (
        f"Required CSV artifact missing: {path}"
    )

    assert path.stat().st_size > 0, (
        f"CSV artifact is empty: {path}"
    )

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(
            csv.DictReader(file)
        )


# =====================================================
# CASE 1
# EXPERIMENT 09 ARTIFACT
# =====================================================

def test_experiment_09_artifact():

    rows = load_csv(
        BENCHMARK_FILE
    )

    assert len(rows) > 0

    required_columns = {
        "similarity",
        "risk_v1_score",
        "risk_v2_score",
    }

    assert required_columns.issubset(
        rows[0].keys()
    )


# =====================================================
# CASE 2
# EXPERIMENT 10 EVIDENCE
# =====================================================

def test_experiment_10_evidence():

    candidates = [
        TESTS_DIR
        / "experiment_10_report.json",

        TESTS_DIR
        / "experiment_10_summary.csv",

        TESTS_DIR
        / "experiment_10_report.csv",

        TESTS_DIR
        / "experiment_10_evidence.json",
    ]

    existing = [
        path
        for path in candidates
        if path.exists()
        and path.stat().st_size > 0
    ]

    # Experiment 10 must have at least one
    # persisted evidence artifact.
    assert len(existing) >= 1


# =====================================================
# CASE 3
# EXPERIMENT 11 ARTIFACT
# =====================================================

def test_experiment_11_artifact():

    rows = load_csv(
        MULTI_DOCUMENT_FILE
    )

    assert len(rows) == 4

    required_columns = {
        "document_id",
        "compared_document_id",
        "similarity",
        "risk_v1_score",
        "risk_v2_score",
        "risk_v1_level",
        "risk_v2_level",
        "v1_v2_difference",
        "alert_severity",
    }

    assert required_columns.issubset(
        rows[0].keys()
    )


# =====================================================
# CASE 4
# EXPERIMENT 12 ARTIFACTS
# =====================================================

def test_experiment_12_artifacts():

    statistics = load_json(
        STATISTICS_FILE
    )

    summary = load_csv(
        SUMMARY_FILE
    )

    assert (
        statistics["project"]
        == "EXAMGUARD AI"
    )

    assert (
        statistics["experiment"]
        == "Experiment 12"
    )

    assert (
        statistics["dataset"][
            "number_of_evaluations"
        ]
        == 4
    )

    assert len(summary) == 1

    summary_row = summary[0]

    assert (
        int(
            summary_row["evaluations"]
        )
        == 4
    )


# =====================================================
# CASE 5
# EXPERIMENT 13 ARTIFACT
# =====================================================

def test_experiment_13_artifact():

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

    required_checks = [
        "text_analysis",
        "similarity",
        "risk_v1",
        "risk_v2",
        "alert",
        "analytics",
    ]

    for check in required_checks:
        assert (
            reproducibility[check]
            is True
        )


# =====================================================
# CASE 6
# EXPERIMENT 14 ARTIFACTS
# =====================================================

def test_experiment_14_artifacts():

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    matrix = load_csv(
        EVIDENCE_MATRIX_FILE
    )

    assert (
        final_evidence["project"]
        == "EXAMGUARD AI"
    )

    assert (
        final_evidence["experiment"]
        == "Experiment 14"
    )

    assert (
        final_evidence["status"]
        == "PASSED"
    )

    assert len(matrix) == 5


# =====================================================
# CASE 7
# CORE RESULT CONSISTENCY
# =====================================================

def test_core_result_consistency():

    reproducibility = load_json(
        REPRODUCIBILITY_FILE
    )

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    reproducibility_results = (
        reproducibility[
            "validated_results"
        ]
    )

    benchmark = (
        final_evidence["benchmark"]
    )

    assert (
        reproducibility_results[
            "similarity"
        ]
        == benchmark["similarity"]
    )

    assert (
        reproducibility_results[
            "risk_v1_score"
        ]
        == benchmark["risk_v1_score"]
    )

    assert (
        reproducibility_results[
            "risk_v2_score"
        ]
        == benchmark["risk_v2_score"]
    )

    assert (
        reproducibility_results[
            "v1_v2_difference"
        ]
        == benchmark[
            "v1_v2_difference"
        ]
    )

    assert (
        reproducibility_results[
            "alert_type"
        ]
        == benchmark[
            "alert_type"
        ]
    )

    assert (
        reproducibility_results[
            "alert_severity"
        ]
        == benchmark[
            "alert_severity"
        ]
    )


# =====================================================
# CASE 8
# FINAL BENCHMARK VALUES
# =====================================================

def test_final_benchmark_values():

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    benchmark = (
        final_evidence["benchmark"]
    )

    assert (
        benchmark["similarity"]
        == 43.325
    )

    assert (
        benchmark["risk_v1_score"]
        == 50.0
    )

    assert (
        benchmark["risk_v1_level"]
        == "medium"
    )

    assert (
        benchmark["risk_v2_score"]
        == 46.0
    )

    assert (
        benchmark["risk_v2_level"]
        == "medium"
    )

    assert (
        benchmark["v1_v2_difference"]
        == -4.0
    )

    assert (
        benchmark["alert_type"]
        == "moderate_risk"
    )

    assert (
        benchmark["alert_severity"]
        == "medium"
    )


# =====================================================
# CASE 9
# EVIDENCE SOURCE COMPLETENESS
# =====================================================

def test_evidence_source_completeness():

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    sources = set(
        final_evidence[
            "evidence_sources"
        ]
    )

    expected = {
        "Experiment 09",
        "Experiment 10",
        "Experiment 11",
        "Experiment 12",
        "Experiment 13",
    }

    assert sources == expected


# =====================================================
# CASE 10
# RESEARCH CONCLUSION VALIDATION
# =====================================================

def test_research_conclusion():

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    conclusion = str(
        final_evidence[
            "research_conclusion"
        ]
    )

    assert len(conclusion) > 50

    assert (
        "EXAMGUARD AI"
        in conclusion
    )

    conclusion_lower = (
        conclusion.lower()
    )

    # The conclusion must communicate
    # consistency/repeated evaluation.
    assert any(
        term in conclusion_lower
        for term in [
            "consistent",
            "consistency",
            "repeated evaluation",
            "repeated",
            "reproduc",
        ]
    )

    assert (
        "pipeline"
        in conclusion_lower
    )


# =====================================================
# CASE 11
# RESEARCH LIMITATION VALIDATION
# =====================================================

def test_research_limitation():

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    limitation = str(
        final_evidence[
            "research_limitation"
        ]
    )

    assert len(limitation) > 50

    limitation_lower = (
        limitation.lower()
    )

    assert (
        "accuracy"
        in limitation_lower
    )

    assert (
        "generalization"
        in limitation_lower
    )


# =====================================================
# CASE 12
# PUBLICATION READINESS MATRIX
# =====================================================

def test_create_publication_readiness_matrix():

    rows = [
        {
            "criterion":
                "Benchmark Evidence",
            "source":
                "Experiment 09",
            "status":
                "READY",
        },
        {
            "criterion":
                "Experimental Evidence",
            "source":
                "Experiment 10",
            "status":
                "READY",
        },
        {
            "criterion":
                "Multi-Document Evaluation",
            "source":
                "Experiment 11",
            "status":
                "READY",
        },
        {
            "criterion":
                "Statistical Analysis",
            "source":
                "Experiment 12",
            "status":
                "READY",
        },
        {
            "criterion":
                "Reproducibility",
            "source":
                "Experiment 13",
            "status":
                "READY",
        },
        {
            "criterion":
                "Evidence Consolidation",
            "source":
                "Experiment 14",
            "status":
                "READY",
        },
        {
            "criterion":
                "Research Limitations",
            "source":
                "Experiment 14",
            "status":
                "READY",
        },
    ]

    with open(
        FINAL_MATRIX_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "criterion",
                "source",
                "status",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    assert FINAL_MATRIX_FILE.exists()

    assert (
        FINAL_MATRIX_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 13
# MATRIX VALIDATION
# =====================================================

def test_publication_readiness_matrix():

    test_create_publication_readiness_matrix()

    rows = load_csv(
        FINAL_MATRIX_FILE
    )

    assert len(rows) == 7

    expected_criteria = {
        "Benchmark Evidence",
        "Experimental Evidence",
        "Multi-Document Evaluation",
        "Statistical Analysis",
        "Reproducibility",
        "Evidence Consolidation",
        "Research Limitations",
    }

    actual_criteria = {
        row["criterion"]
        for row in rows
    }

    assert (
        actual_criteria
        == expected_criteria
    )

    assert all(
        row["status"] == "READY"
        for row in rows
    )


# =====================================================
# CASE 14
# BUILD FINAL RESEARCH PACKAGE
# =====================================================

def test_create_final_research_package():

    statistics = load_json(
        STATISTICS_FILE
    )

    final_evidence = load_json(
        FINAL_EVIDENCE_FILE
    )

    reproducibility = load_json(
        REPRODUCIBILITY_FILE
    )

    package = {

        "project":
            "EXAMGUARD AI",

        "package":
            "Final Research Package",

        "experiment":
            "Experiment 15",

        "status":
            "READY",

        "publication_readiness":
            True,

        "validated_experiments": [
            "Experiment 09",
            "Experiment 10",
            "Experiment 11",
            "Experiment 12",
            "Experiment 13",
            "Experiment 14",
        ],

        "core_benchmark": (
            final_evidence[
                "benchmark"
            ]
        ),

        "statistical_summary": {
            "evaluations":
                statistics[
                    "dataset"
                ][
                    "number_of_evaluations"
                ],

            "average_similarity":
                statistics[
                    "similarity"
                ][
                    "mean"
                ],

            "average_risk_v1":
                statistics[
                    "risk_v1"
                ][
                    "mean"
                ],

            "average_risk_v2":
                statistics[
                    "risk_v2"
                ][
                    "mean"
                ],

            "average_v1_v2_difference":
                statistics[
                    "v1_vs_v2"
                ][
                    "mean_difference"
                ],
        },

        "reproducibility":
            reproducibility[
                "reproducibility"
            ],

        "research_conclusion":
            final_evidence[
                "research_conclusion"
            ],

        "research_limitation":
            final_evidence[
                "research_limitation"
            ],

        "publication_statement": (
            "The current evidence package "
            "is internally consistent and "
            "suitable as a documented "
            "experimental evidence package. "
            "Claims remain limited to the "
            "evaluated cases and do not imply "
            "population-level model performance."
        ),

        "artifact_manifest": [
            "experiment_09_results.csv",
            "experiment_11_multi_document_results.csv",
            "experiment_12_statistics.json",
            "experiment_12_summary.csv",
            "experiment_13_reproducibility_report.json",
            "experiment_14_final_evidence.json",
            "experiment_14_evidence_matrix.csv",
        ],
    }

    with open(
        FINAL_PACKAGE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            package,
            file,
            indent=4,
        )

    assert FINAL_PACKAGE_FILE.exists()

    assert (
        FINAL_PACKAGE_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 15
# FINAL PACKAGE INTEGRITY
# =====================================================

def test_final_package_integrity():

    test_create_final_research_package()

    package = load_json(
        FINAL_PACKAGE_FILE
    )

    assert (
        package["project"]
        == "EXAMGUARD AI"
    )

    assert (
        package["experiment"]
        == "Experiment 15"
    )

    assert (
        package["status"]
        == "READY"
    )

    assert (
        package[
            "publication_readiness"
        ]
        is True
    )

    assert (
        len(
            package[
                "validated_experiments"
            ]
        )
        == 6
    )

    benchmark = package[
        "core_benchmark"
    ]

    assert (
        benchmark["similarity"]
        == 43.325
    )

    assert (
        benchmark["risk_v1_score"]
        == 50.0
    )

    assert (
        benchmark["risk_v1_level"]
        == "medium"
    )

    assert (
        benchmark["risk_v2_score"]
        == 46.0
    )

    assert (
        benchmark["risk_v2_level"]
        == "medium"
    )

    assert (
        benchmark["v1_v2_difference"]
        == -4.0
    )

    assert (
        benchmark["alert_type"]
        == "moderate_risk"
    )

    assert (
        benchmark["alert_severity"]
        == "medium"
    )

    assert (
        len(
            package[
                "artifact_manifest"
            ]
        )
        >= 7
    )

    # Final package must contain a research
    # limitation statement.
    assert len(
        package[
            "research_limitation"
        ]
    ) > 50