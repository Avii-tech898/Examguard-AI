from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from backend.models import (
    Document,
    DocumentText,
    AnalysisResult,
    SimilarityResult,
    RiskScore,
    Alert,
)

from backend.services.document_extractor import extract_text_from_pdf
from backend.services.nlp_analyzer import analyze_text
from backend.services.similarity_engine import calculate_similarity
from backend.services.risk_engine import (
    calculate_risk,
    calculate_feature_based_risk,
)
from backend.services.feature_engine import (
    build_document_features,
)
from backend.services.alert_engine import generate_alert


UPLOAD_DIR = Path("uploads/documents")


def _get_document(
    document_id: int,
    db: Session,
) -> Document:

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise ValueError(
            f"Document {document_id} not found"
        )

    return document


def _extract_or_get_text(
    document: Document,
    db: Session,
) -> DocumentText:

    existing_text = (
        db.query(DocumentText)
        .filter(
            DocumentText.document_id == document.id
        )
        .first()
    )

    if existing_text and existing_text.extracted_text:
        return existing_text

    file_path = (
        UPLOAD_DIR / document.file_name
    )

    if not file_path.exists():
        raise ValueError(
            f"Document file not found: "
            f"{document.file_name}"
        )

    try:
        extracted_text = extract_text_from_pdf(
            str(file_path)
        )
    except Exception as exc:
        raise ValueError(
            f"Text extraction failed for "
            f"document {document.id}: {exc}"
        )

    if not extracted_text or not extracted_text.strip():
        raise ValueError(
            f"No text could be extracted from "
            f"document {document.id}"
        )

    if existing_text:
        existing_text.extracted_text = (
            extracted_text
        )
        existing_text.ocr_engine = "pypdf"
        existing_text.ocr_confidence = 100.00
        existing_text.language = "en"

        document_text = existing_text

    else:
        document_text = DocumentText(
            document_id=document.id,
            extracted_text=extracted_text,
            ocr_engine="pypdf",
            ocr_confidence=100.00,
            language="en",
        )

        db.add(document_text)

    db.flush()

    return document_text


def _create_or_update_analysis(
    document_id: int,
    text: str,
    db: Session,
) -> AnalysisResult:

    analysis_data = analyze_text(text)

    existing_result = (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.document_id
            == document_id,
            AnalysisResult.analysis_type
            == "nlp_basic",
        )
        .order_by(
            AnalysisResult.id.desc()
        )
        .first()
    )

    if existing_result:

        existing_result.result_data = (
            analysis_data
        )

        existing_result.model_version = (
            "nlp-basic-v1"
        )

        existing_result.confidence_score = (
            100.00
        )

        result = existing_result

    else:

        result = AnalysisResult(
            document_id=document_id,
            analysis_type="nlp_basic",
            result_data=analysis_data,
            model_version="nlp-basic-v1",
            confidence_score=100.00,
        )

        db.add(result)

    db.flush()

    return result


def _create_or_update_similarity(
    document_id: int,
    compared_document_id: int,
    text_a: str,
    text_b: str,
    db: Session,
) -> SimilarityResult:

    similarity_score = calculate_similarity(
        text_a,
        text_b,
    )

    existing_result = (
        db.query(SimilarityResult)
        .filter(
            SimilarityResult.document_id
            == document_id,
            SimilarityResult.compared_document_id
            == compared_document_id,
        )
        .order_by(
            SimilarityResult.id.desc()
        )
        .first()
    )

    if existing_result:

        existing_result.similarity_score = (
            similarity_score
        )

        existing_result.similarity_method = (
            "tfidf_cosine"
        )

        result = existing_result

    else:

        result = SimilarityResult(
            document_id=document_id,
            compared_document_id=compared_document_id,
            similarity_score=similarity_score,
            similarity_method="tfidf_cosine",
        )

        db.add(result)

    db.flush()

    return result


def _save_risk(
    document_id: int,
    risk_data: dict[str, Any],
    risk_factors: list[Any],
    db: Session,
) -> RiskScore:

    risk_score = RiskScore(
        document_id=document_id,
        risk_score=risk_data["risk_score"],
        risk_level=risk_data["risk_level"],
        risk_factors=risk_factors,
        model_version=risk_data["model_version"],
    )

    db.add(risk_score)
    db.flush()

    return risk_score


def _create_or_update_alert(
    document_id: int,
    risk_score: RiskScore,
    db: Session,
) -> Alert:

    alert_data = generate_alert(
        risk_score=float(
            risk_score.risk_score
        ),
        risk_level=risk_score.risk_level,
        risk_factors=risk_score.risk_factors,
    )

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.document_id == document_id,
            Alert.risk_score_id == risk_score.id,
            Alert.status == "open",
        )
        .order_by(
            Alert.id.desc()
        )
        .first()
    )

    if existing_alert:

        existing_alert.alert_type = (
            alert_data["alert_type"]
        )

        existing_alert.severity = (
            alert_data["severity"]
        )

        existing_alert.message = (
            alert_data["message"]
        )

        existing_alert.status = (
            alert_data["status"]
        )

        existing_alert.resolved_at = None

        alert = existing_alert

    else:

        alert = Alert(
            document_id=document_id,
            risk_score_id=risk_score.id,
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            status=alert_data["status"],
            resolved_at=None,
        )

        db.add(alert)

    db.flush()

    return alert


def process_document_pair(
    document_id: int,
    compared_document_id: int,
    db: Session,
) -> dict[str, Any]:

    # =====================================================
    # VALIDATION
    # =====================================================

    if document_id == compared_document_id:
        raise ValueError(
            "A document cannot be compared "
            "with itself"
        )

    current_document = _get_document(
        document_id,
        db,
    )

    compared_document = _get_document(
        compared_document_id,
        db,
    )

    # =====================================================
    # 1. TEXT EXTRACTION
    # =====================================================

    current_text = _extract_or_get_text(
        current_document,
        db,
    )

    compared_text = _extract_or_get_text(
        compared_document,
        db,
    )

    # =====================================================
    # 2. NLP ANALYSIS
    # =====================================================

    current_analysis = _create_or_update_analysis(
        document_id,
        current_text.extracted_text,
        db,
    )

    compared_analysis = _create_or_update_analysis(
        compared_document_id,
        compared_text.extracted_text,
        db,
    )

    # =====================================================
    # 3. SIMILARITY
    # =====================================================

    similarity_result = _create_or_update_similarity(
        document_id,
        compared_document_id,
        current_text.extracted_text,
        compared_text.extracted_text,
        db,
    )

    similarity_score = float(
        similarity_result.similarity_score
    )

    # =====================================================
    # 4. RISK V1
    # =====================================================

    risk_v1_data = calculate_risk(
        similarity_score
    )

    risk_v1 = _save_risk(
        document_id=document_id,
        risk_data=risk_v1_data,
        risk_factors=list(
            risk_v1_data["risk_factors"]
        ),
        db=db,
    )

    # =====================================================
    # 5. RISK V2 FEATURES
    # =====================================================

    features = build_document_features(
        current_analysis={
            "result_data":
                current_analysis.result_data
        },
        compared_analysis={
            "result_data":
                compared_analysis.result_data
        },
        similarity_score=similarity_score,
    )

    # =====================================================
    # 6. RISK V2
    # =====================================================

    risk_v2_data = calculate_feature_based_risk(
        features
    )

    risk_v2_data["model_version"] = (
        "risk-rule-v2"
    )

    risk_v2_factors = list(
        risk_v2_data["risk_factors"]
    )

    risk_v2_factors.append(
        {
            "feature_snapshot": features
        }
    )

    risk_v2 = _save_risk(
        document_id=document_id,
        risk_data=risk_v2_data,
        risk_factors=risk_v2_factors,
        db=db,
    )

    # =====================================================
    # 7. ALERT
    # =====================================================

    alert = _create_or_update_alert(
        document_id=document_id,
        risk_score=risk_v2,
        db=db,
    )

    # =====================================================
    # SAVE EVERYTHING
    # =====================================================

    db.commit()

    db.refresh(current_text)
    db.refresh(compared_text)

    db.refresh(current_analysis)
    db.refresh(compared_analysis)

    db.refresh(similarity_result)

    db.refresh(risk_v1)
    db.refresh(risk_v2)

    db.refresh(alert)

    # =====================================================
    # COMPLETE RESULT
    # =====================================================

    return {
        "status": "completed",

        "document": {
            "id": current_document.id,
            "file_name":
                current_document.file_name,
        },

        "compared_document": {
            "id": compared_document.id,
            "file_name":
                compared_document.file_name,
        },

        "text_extraction": {
            "current_document": "completed",
            "compared_document": "completed",
        },

        "nlp_analysis": {
            "current_document": "completed",
            "compared_document": "completed",
        },

        "similarity": {
            "score": similarity_score,
            "method":
                similarity_result.similarity_method,
            "status": "completed",
        },

        "risk_v1": {
            "id": risk_v1.id,
            "score": float(
                risk_v1.risk_score
            ),
            "level": risk_v1.risk_level,
            "model":
                risk_v1.model_version,
        },

        "risk_v2": {
            "id": risk_v2.id,
            "score": float(
                risk_v2.risk_score
            ),
            "level": risk_v2.risk_level,
            "model":
                risk_v2.model_version,
            "features": features,
        },

        "alert": {
            "id": alert.id,
            "type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
        },
    }