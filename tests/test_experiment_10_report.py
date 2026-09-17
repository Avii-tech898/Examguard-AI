import csv
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 10
# FINAL EXPERIMENTAL REPORT
# & EVIDENCE CONSOLIDATION
# =====================================================

DOCUMENT_ID = 4
COMPARED_DOCUMENT_ID = 3

TESTS_DIR = Path(__file__).resolve().parent

BENCHMARK_FILE = (
    TESTS_DIR / "experiment_09_results.csv"
)

REPORT_FILE = (
    TESTS_DIR / "experiment_10_report.json"
)

SUMMARY_FILE = (
    TESTS_DIR / "experiment_10_summary.csv"
)


# =====================================================
# HELPER
# =====================================================

def get_json(endpoint):
    response = client.get(endpoint)

    assert response.status_code == 200

    return response.json()


# =====================================================
# CASE 1
# COLLECT SYSTEM RESULTS
# =====================================================

def test_collect_system_results():
    """
    Collect the current real-document evaluation
    from the EXAMGUARD-AI API.
    """

    text = get_json(
        f"/api/documents/{DOCUMENT_ID}/text"
    )

    analysis = get_json(
        f"/api/documents/{DOCUMENT_ID}/analysis"
    )

    similarity = get_json(
        f"/api/documents/"
        f"{DOCUMENT_ID}/similarity/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    alert = get_json(
        f"/api/documents/{DOCUMENT_ID}/alerts"
    )

    analytics = get_json(
        "/api/analytics/overview"
    )

    assert text["document_id"] == DOCUMENT_ID

    assert (
        len(
            text["extracted_text"].strip()
        )
        > 0
    )

    assert (
        analysis["analysis_type"]
        == "nlp_basic"
    )

    assert (
        similarity["document_id"]
        == DOCUMENT_ID
    )

    assert (
        similarity["compared_document_id"]
        == COMPARED_DOCUMENT_ID
    )

    assert (
        0
        <= float(
            similarity["similarity_score"]
        )
        <= 100
    )

    assert (
        risk_v1["model_version"]
        == "risk-rule-v1"
    )

    assert (
        risk_v2["model_version"]
        == "risk-rule-v2"
    )

    assert (
        alert["document_id"]
        == DOCUMENT_ID
    )

    assert (
        analytics["total_documents"]
        >= 4
    )


# =====================================================
# CASE 2
# VALIDATE CORE BENCHMARK
# =====================================================

def test_validate_core_benchmark():
    """
    Validate the known benchmark values from
    Experiment 09.
    """

    similarity = get_json(
        f"/api/documents/"
        f"{DOCUMENT_ID}/similarity/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    assert round(
        float(
            similarity["similarity_score"]
        ),
        3,
    ) == 43.325

    assert (
        float(
            risk_v1["risk_score"]
        )
        == 50.0
    )

    assert (
        risk_v1["risk_level"]
        == "medium"
    )

    assert (
        float(
            risk_v2["risk_score"]
        )
        == 46.0
    )

    assert (
        risk_v2["risk_level"]
        == "medium"
    )


# =====================================================
# CASE 3
# V1 VS V2 RESEARCH FINDING
# =====================================================

def test_v1_vs_v2_research_finding():
    """
    Validate the observed V1 → V2 score difference.
    """

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    v1_score = float(
        risk_v1["risk_score"]
    )

    v2_score = float(
        risk_v2["risk_score"]
    )

    difference = round(
        v2_score - v1_score,
        2,
    )

    assert difference == -4.0

    assert (
        risk_v1["risk_level"]
        == risk_v2["risk_level"]
        == "medium"
    )


# =====================================================
# CASE 4
# ALERT RESEARCH FINDING
# =====================================================

def test_alert_research_finding():
    """
    Validate that the alert corresponds to the
    observed medium-risk evaluation.
    """

    alert = get_json(
        f"/api/documents/{DOCUMENT_ID}/alerts"
    )

    assert (
        alert["severity"]
        == "medium"
    )

    assert (
        alert["alert_type"]
        == "moderate_risk"
    )

    assert (
        alert["status"]
        in {
            "open",
            "resolved",
        }
    )


# =====================================================
# CASE 5
# ANALYTICS RESEARCH FINDING
# =====================================================

def test_analytics_research_finding():
    """
    Validate the current system-level analytics.
    """

    analytics = get_json(
        "/api/analytics/overview"
    )

    assert (
        analytics["total_documents"]
        >= 4
    )

    assert (
        analytics["analyzed_documents"]
        >= 4
    )

    assert (
        analytics["similarity_comparisons"]
        >= 1
    )

    assert (
        0
        <= float(
            analytics["average_similarity"]
        )
        <= 100
    )

    assert (
        0
        <= float(
            analytics["processing_rate"]
        )
        <= 100
    )

    assert (
        analytics["analytics_status"]
        == "active"
    )


# =====================================================
# CASE 6
# BUILD JSON RESEARCH REPORT
# =====================================================

def test_build_json_research_report():
    """
    Create a structured research evidence report.
    """

    text = get_json(
        f"/api/documents/{DOCUMENT_ID}/text"
    )

    analysis = get_json(
        f"/api/documents/{DOCUMENT_ID}/analysis"
    )

    similarity = get_json(
        f"/api/documents/"
        f"{DOCUMENT_ID}/similarity/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    alert = get_json(
        f"/api/documents/{DOCUMENT_ID}/alerts"
    )

    analytics = get_json(
        "/api/analytics/overview"
    )

    report = {
        "project": "EXAMGUARD AI",
        "experiment": "Experiment 10",
        "title": (
            "Final Experimental Report "
            "and Evidence Consolidation"
        ),
        "version": "0.1.0",

        "evaluation": {
            "document_id": DOCUMENT_ID,
            "compared_document_id": (
                COMPARED_DOCUMENT_ID
            ),
        },

        "text_extraction": {
            "status": "completed",
            "ocr_engine": text.get(
                "ocr_engine"
            ),
            "language": text.get(
                "language"
            ),
            "ocr_confidence": text.get(
                "ocr_confidence"
            ),
            "character_count": len(
                text[
                    "extracted_text"
                ]
            ),
        },

        "nlp_analysis": {
            "analysis_type": (
                analysis[
                    "analysis_type"
                ]
            ),
            "model_version": (
                analysis[
                    "model_version"
                ]
            ),
            "confidence_score": (
                analysis[
                    "confidence_score"
                ]
            ),
            "word_count": (
                analysis[
                    "result_data"
                ]["word_count"]
            ),
            "sentence_count": (
                analysis[
                    "result_data"
                ]["sentence_count"]
            ),
            "unique_word_count": (
                analysis[
                    "result_data"
                ]["unique_word_count"]
            ),
        },

        "similarity": {
            "score": round(
                float(
                    similarity[
                        "similarity_score"
                    ]
                ),
                3,
            ),
            "method": similarity[
                "similarity_method"
            ],
        },

        "risk_v1": {
            "score": float(
                risk_v1["risk_score"]
            ),
            "level": risk_v1[
                "risk_level"
            ],
            "model": risk_v1[
                "model_version"
            ],
        },

        "risk_v2": {
            "score": float(
                risk_v2["risk_score"]
            ),
            "level": risk_v2[
                "risk_level"
            ],
            "model": risk_v2[
                "model_version"
            ],
        },

        "v1_v2_comparison": {
            "score_difference": round(
                float(
                    risk_v2["risk_score"]
                )
                - float(
                    risk_v1["risk_score"]
                ),
                2,
            ),
            "risk_level_changed": (
                risk_v1["risk_level"]
                != risk_v2["risk_level"]
            ),
        },

        "alert": {
            "type": alert[
                "alert_type"
            ],
            "severity": alert[
                "severity"
            ],
            "status": alert[
                "status"
            ],
        },

        "analytics": {
            "total_documents": (
                analytics[
                    "total_documents"
                ]
            ),
            "analyzed_documents": (
                analytics[
                    "analyzed_documents"
                ]
            ),
            "similarity_comparisons": (
                analytics[
                    "similarity_comparisons"
                ]
            ),
            "average_similarity": (
                analytics[
                    "average_similarity"
                ]
            ),
            "processing_rate": (
                analytics[
                    "processing_rate"
                ]
            ),
            "analytics_status": (
                analytics[
                    "analytics_status"
                ]
            ),
        },

        "findings": [
            (
                "The evaluated document pair "
                "shows moderate similarity."
            ),
            (
                "Risk V2 produced a lower score "
                "than Risk V1 for this case."
            ),
            (
                "Both risk versions classified "
                "the document pair as medium risk."
            ),
            (
                "The alert engine generated a "
                "moderate-risk alert."
            ),
            (
                "The analytics layer reports "
                "an active system state."
            ),
        ],

        "limitations": [
            (
                "The benchmark uses the currently "
                "available real-document pair."
            ),
            (
                "The observed result should not be "
                "interpreted as population-level "
                "model accuracy."
            ),
            (
                "Processing time is environment "
                "dependent."
            ),
        ],
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )

    assert REPORT_FILE.exists()

    assert REPORT_FILE.stat().st_size > 0


# =====================================================
# CASE 7
# VALIDATE JSON REPORT
# =====================================================

def test_validate_json_report():
    """
    Validate the generated JSON research report.
    """

    test_build_json_research_report()

    with open(
        REPORT_FILE,
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
        == "Experiment 10"
    )

    assert (
        report["similarity"]["score"]
        == 43.325
    )

    assert (
        report["risk_v1"]["score"]
        == 50.0
    )

    assert (
        report["risk_v2"]["score"]
        == 46.0
    )

    assert (
        report[
            "v1_v2_comparison"
        ]["score_difference"]
        == -4.0
    )

    assert (
        report[
            "v1_v2_comparison"
        ]["risk_level_changed"]
        is False
    )


# =====================================================
# CASE 8
# BUILD SUMMARY CSV
# =====================================================

def test_build_summary_csv():
    """
    Create a compact research summary table.
    """

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    similarity = get_json(
        f"/api/documents/"
        f"{DOCUMENT_ID}/similarity/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    alert = get_json(
        f"/api/documents/{DOCUMENT_ID}/alerts"
    )

    row = {
        "document_id": DOCUMENT_ID,
        "compared_document_id": (
            COMPARED_DOCUMENT_ID
        ),
        "similarity_score": round(
            float(
                similarity[
                    "similarity_score"
                ]
            ),
            3,
        ),
        "similarity_method": similarity[
            "similarity_method"
        ],
        "risk_v1_score": float(
            risk_v1["risk_score"]
        ),
        "risk_v1_level": risk_v1[
            "risk_level"
        ],
        "risk_v2_score": float(
            risk_v2["risk_score"]
        ),
        "risk_v2_level": risk_v2[
            "risk_level"
        ],
        "v1_v2_difference": round(
            float(
                risk_v2["risk_score"]
            )
            - float(
                risk_v1["risk_score"]
            ),
            2,
        ),
        "alert_type": alert[
            "alert_type"
        ],
        "alert_severity": alert[
            "severity"
        ],
    }

    fieldnames = list(row.keys())

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerow(row)

    assert SUMMARY_FILE.exists()

    assert SUMMARY_FILE.stat().st_size > 0


# =====================================================
# CASE 9
# SUMMARY CSV VALIDATION
# =====================================================

def test_summary_csv_validation():
    """
    Validate the final summary table.
    """

    test_build_summary_csv()

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
        int(row["document_id"])
        == 4
    )

    assert (
        int(
            row[
                "compared_document_id"
            ]
        )
        == 3
    )

    assert (
        float(
            row["similarity_score"]
        )
        == 43.325
    )

    assert (
        float(
            row["risk_v1_score"]
        )
        == 50.0
    )

    assert (
        float(
            row["risk_v2_score"]
        )
        == 46.0
    )

    assert (
        float(
            row["v1_v2_difference"]
        )
        == -4.0
    )

    assert (
        row["risk_v1_level"]
        == "medium"
    )

    assert (
        row["risk_v2_level"]
        == "medium"
    )

    assert (
        row["alert_severity"]
        == "medium"
    )


# =====================================================
# CASE 10
# FINAL EVIDENCE INTEGRITY
# =====================================================

def test_final_evidence_integrity():
    """
    Final consistency check across the complete
    experimental evidence chain.
    """

    similarity = get_json(
        f"/api/documents/"
        f"{DOCUMENT_ID}/similarity/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    risk_v1 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v1"
    )

    risk_v2 = get_json(
        f"/api/documents/{DOCUMENT_ID}/risk-v2"
    )

    alert = get_json(
        f"/api/documents/{DOCUMENT_ID}/alerts"
    )

    assert (
        round(
            float(
                similarity[
                    "similarity_score"
                ]
            ),
            3,
        )
        == 43.325
    )

    assert (
        float(
            risk_v1["risk_score"]
        )
        == 50.0
    )

    assert (
        float(
            risk_v2["risk_score"]
        )
        == 46.0
    )

    assert (
        round(
            float(
                risk_v2["risk_score"]
            )
            - float(
                risk_v1["risk_score"]
            ),
            2,
        )
        == -4.0
    )

    assert (
        risk_v1["risk_level"]
        == risk_v2["risk_level"]
        == "medium"
    )

    assert (
        alert["severity"]
        == "medium"
    )

    assert (
        alert["alert_type"]
        == "moderate_risk"
    )