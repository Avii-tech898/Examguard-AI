import csv
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# =====================================================
# EXPERIMENT 13
# END-TO-END REPRODUCIBILITY
# & FINAL REGRESSION
# =====================================================

DOCUMENT_ID = 4
COMPARED_DOCUMENT_ID = 3

TESTS_DIR = Path(__file__).resolve().parent

REPORT_FILE = (
    TESTS_DIR
    / "experiment_13_reproducibility_report.json"
)


# =====================================================
# HELPERS
# =====================================================

def get_json(endpoint):
    response = client.get(endpoint)

    assert response.status_code == 200

    return response.json()


def collect_pipeline_state():
    """
    Collect all major outputs for one real-document
    evaluation.
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

    return {
        "text": {
            "document_id": text["document_id"],
            "text_length": len(
                text["extracted_text"]
            ),
            "ocr_engine": text.get(
                "ocr_engine"
            ),
            "language": text.get(
                "language"
            ),
            "ocr_confidence": text.get(
                "ocr_confidence"
            ),
        },

        "analysis": {
            "analysis_type": analysis[
                "analysis_type"
            ],
            "model_version": analysis[
                "model_version"
            ],
            "word_count": analysis[
                "result_data"
            ]["word_count"],
            "sentence_count": analysis[
                "result_data"
            ]["sentence_count"],
            "unique_word_count": analysis[
                "result_data"
            ]["unique_word_count"],
        },

        "similarity": {
            "document_id": similarity[
                "document_id"
            ],
            "compared_document_id": similarity[
                "compared_document_id"
            ],
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
            "total_documents": analytics[
                "total_documents"
            ],
            "analyzed_documents": analytics[
                "analyzed_documents"
            ],
            "similarity_comparisons": analytics[
                "similarity_comparisons"
            ],
            "processing_rate": analytics[
                "processing_rate"
            ],
            "analytics_status": analytics[
                "analytics_status"
            ],
        },
    }


def run_pipeline():
    """
    Execute the complete processing pipeline.
    """

    response = client.post(
        f"/api/documents/"
        f"{DOCUMENT_ID}/process/"
        f"{COMPARED_DOCUMENT_ID}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"

    return data


# =====================================================
# CASE 1
# SYSTEM ROOT
# =====================================================

def test_system_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "EXAMGUARD AI"
    assert data["status"] == "online"
    assert data["version"] == "0.1.0"


# =====================================================
# CASE 2
# HEALTH CHECK
# =====================================================

def test_health_endpoint():

    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == (
        "EXAMGUARD AI Backend"
    )


# =====================================================
# CASE 3
# DOCUMENT AVAILABILITY
# =====================================================

def test_real_documents_available():

    response = client.get(
        "/api/documents/"
    )

    assert response.status_code == 200

    documents = response.json()

    ids = {
        int(document["id"])
        for document in documents
    }

    assert DOCUMENT_ID in ids
    assert COMPARED_DOCUMENT_ID in ids


# =====================================================
# CASE 4
# COMPLETE PIPELINE
# =====================================================

def test_complete_pipeline_reproducibility():

    data = run_pipeline()

    assert data["status"] == "completed"

    assert (
        data["document"]["id"]
        == DOCUMENT_ID
    )

    assert (
        data["compared_document"]["id"]
        == COMPARED_DOCUMENT_ID
    )

    assert (
        data["text_extraction"][
            "current_document"
        ]
        == "completed"
    )

    assert (
        data["text_extraction"][
            "compared_document"
        ]
        == "completed"
    )

    assert (
        data["nlp_analysis"][
            "current_document"
        ]
        == "completed"
    )

    assert (
        data["nlp_analysis"][
            "compared_document"
        ]
        == "completed"
    )

    assert (
        data["similarity"]["status"]
        == "completed"
    )


# =====================================================
# CASE 5
# TEXT + NLP REPRODUCIBILITY
# =====================================================

def test_text_nlp_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert (
        first["text"]
        == second["text"]
    )

    assert (
        first["analysis"]
        == second["analysis"]
    )


# =====================================================
# CASE 6
# SIMILARITY REPRODUCIBILITY
# =====================================================

def test_similarity_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert (
        first["similarity"]
        == second["similarity"]
    )

    assert (
        first["similarity"]["score"]
        == 43.325
    )

    assert (
        first["similarity"]["method"]
        == "tfidf_cosine"
    )


# =====================================================
# CASE 7
# RISK V1/V2 REPRODUCIBILITY
# =====================================================

def test_risk_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert (
        first["risk_v1"]
        == second["risk_v1"]
    )

    assert (
        first["risk_v2"]
        == second["risk_v2"]
    )

    assert (
        first["risk_v1"]["score"]
        == 50.0
    )

    assert (
        first["risk_v2"]["score"]
        == 46.0
    )

    assert (
        first["risk_v1"]["level"]
        == "medium"
    )

    assert (
        first["risk_v2"]["level"]
        == "medium"
    )


# =====================================================
# CASE 8
# V1 VS V2 REPRODUCIBILITY
# =====================================================

def test_v1_v2_difference_reproducibility():

    state = collect_pipeline_state()

    difference = round(
        state["risk_v2"]["score"]
        - state["risk_v1"]["score"],
        2,
    )

    assert difference == -4.0

    assert (
        state["risk_v1"]["level"]
        == state["risk_v2"]["level"]
    )


# =====================================================
# CASE 9
# ALERT REPRODUCIBILITY
# =====================================================

def test_alert_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert (
        first["alert"]["type"]
        == second["alert"]["type"]
    )

    assert (
        first["alert"]["severity"]
        == second["alert"]["severity"]
    )

    assert (
        first["alert"]["type"]
        == "moderate_risk"
    )

    assert (
        first["alert"]["severity"]
        == "medium"
    )


# =====================================================
# CASE 10
# ANALYTICS REPRODUCIBILITY
# =====================================================

def test_analytics_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert (
        first["analytics"]
        == second["analytics"]
    )

    assert (
        first["analytics"][
            "total_documents"
        ]
        >= 4
    )

    assert (
        first["analytics"][
            "analyzed_documents"
        ]
        >= 4
    )

    assert (
        first["analytics"][
            "similarity_comparisons"
        ]
        >= 4
    )

    assert (
        first["analytics"][
            "analytics_status"
        ]
        == "active"
    )


# =====================================================
# CASE 11
# FULL STATE REPRODUCIBILITY
# =====================================================

def test_full_state_reproducibility():

    first = collect_pipeline_state()
    second = collect_pipeline_state()

    assert first == second


# =====================================================
# CASE 12
# INVALID INPUT REGRESSION
# =====================================================

def test_invalid_input_regression():

    response = client.get(
        "/api/documents/999999/text"
    )

    assert response.status_code in {
        404,
        400,
    }

    response = client.get(
        "/api/documents/0/text"
    )

    assert response.status_code in {
        404,
        400,
        422,
    }

    response = client.post(
        f"/api/documents/"
        f"{DOCUMENT_ID}/process/"
        f"{DOCUMENT_ID}"
    )

    assert response.status_code in {
        400,
        409,
        422,
    }


# =====================================================
# CASE 13
# BUILD REPRODUCIBILITY REPORT
# =====================================================

def test_create_reproducibility_report():

    state = collect_pipeline_state()

    report = {
        "project": "EXAMGUARD AI",
        "experiment": "Experiment 13",
        "title": (
            "End-to-End Reproducibility "
            "and Final Regression"
        ),
        "version": "0.1.0",

        "evaluation": {
            "document_id": DOCUMENT_ID,
            "compared_document_id": (
                COMPARED_DOCUMENT_ID
            ),
        },

        "reproducibility": {
            "text_analysis": True,
            "similarity": True,
            "risk_v1": True,
            "risk_v2": True,
            "alert": True,
            "analytics": True,
        },

        "validated_results": {
            "similarity": state[
                "similarity"
            ]["score"],

            "risk_v1_score": state[
                "risk_v1"
            ]["score"],

            "risk_v1_level": state[
                "risk_v1"
            ]["level"],

            "risk_v2_score": state[
                "risk_v2"
            ]["score"],

            "risk_v2_level": state[
                "risk_v2"
            ]["level"],

            "v1_v2_difference": round(
                state["risk_v2"]["score"]
                - state["risk_v1"]["score"],
                2,
            ),

            "alert_type": state[
                "alert"
            ]["type"],

            "alert_severity": state[
                "alert"
            ]["severity"],
        },

        "conclusion": (
            "The evaluated real-document pipeline "
            "produced reproducible analytical outputs "
            "across repeated API evaluations."
        ),

        "limitation": (
            "Reproducibility of the evaluated case "
            "does not establish population-level "
            "model accuracy."
        ),
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

    assert (
        REPORT_FILE.stat().st_size
        > 0
    )


# =====================================================
# CASE 14
# FINAL REPORT VALIDATION
# =====================================================

def test_final_report_validation():

    test_create_reproducibility_report()

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
        == "Experiment 13"
    )

    assert (
        report["reproducibility"][
            "text_analysis"
        ]
        is True
    )

    assert (
        report["reproducibility"][
            "similarity"
        ]
        is True
    )

    assert (
        report["reproducibility"][
            "risk_v1"
        ]
        is True
    )

    assert (
        report["reproducibility"][
            "risk_v2"
        ]
        is True
    )

    assert (
        report["reproducibility"][
            "alert"
        ]
        is True
    )

    assert (
        report["reproducibility"][
            "analytics"
        ]
        is True
    )

    assert (
        report[
            "validated_results"
        ]["similarity"]
        == 43.325
    )

    assert (
        report[
            "validated_results"
        ]["risk_v1_score"]
        == 50.0
    )

    assert (
        report[
            "validated_results"
        ]["risk_v2_score"]
        == 46.0
    )

    assert (
        report[
            "validated_results"
        ]["v1_v2_difference"]
        == -4.0
    )

    assert (
        report[
            "validated_results"
        ]["alert_severity"]
        == "medium"
    )


# =====================================================
# CASE 15
# FINAL SYSTEM INTEGRITY
# =====================================================

def test_final_system_integrity():

    state = collect_pipeline_state()

    assert (
        state["text"]["document_id"]
        == DOCUMENT_ID
    )

    assert (
        state["similarity"][
            "document_id"
        ]
        == DOCUMENT_ID
    )

    assert (
        state["similarity"][
            "compared_document_id"
        ]
        == COMPARED_DOCUMENT_ID
    )

    assert (
        state["risk_v1"]["model"]
        == "risk-rule-v1"
    )

    assert (
        state["risk_v2"]["model"]
        == "risk-rule-v2"
    )

    assert (
        state["risk_v1"]["level"]
        == "medium"
    )

    assert (
        state["risk_v2"]["level"]
        == "medium"
    )

    assert (
        state["alert"]["severity"]
        == "medium"
    )

    assert (
        state["analytics"][
            "analytics_status"
        ]
        == "active"
    )