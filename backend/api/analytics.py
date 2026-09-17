from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import (
    Document,
    AnalysisResult,
    SimilarityResult,
    RiskScore,
    Alert,
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
):
    """
    EXAMGUARD-AI Security Analytics Overview.

    Provides live analytics calculated from the
    existing database tables.

    Existing response fields are preserved for
    frontend compatibility.
    """

    # =====================================================
    # 1. TOTAL DOCUMENTS
    # =====================================================

    total_documents = (
        db.query(func.count(Document.id))
        .scalar()
        or 0
    )

    # =====================================================
    # 2. ANALYZED DOCUMENTS
    # =====================================================

    analyzed_documents = (
        db.query(
            func.count(
                func.distinct(
                    AnalysisResult.document_id
                )
            )
        )
        .filter(
            AnalysisResult.analysis_type == "nlp_basic"
        )
        .scalar()
        or 0
    )

    # =====================================================
    # 3. SIMILARITY COMPARISONS
    # =====================================================

    similarity_comparisons = (
        db.query(
            func.count(SimilarityResult.id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # 4. AVERAGE SIMILARITY
    # =====================================================

    average_similarity = (
        db.query(
            func.avg(
                SimilarityResult.similarity_score
            )
        )
        .scalar()
    )

    if average_similarity is None:
        average_similarity = 0.0
    else:
        average_similarity = round(
            float(average_similarity),
            2,
        )

    # =====================================================
    # 5. LATEST RISK PER DOCUMENT
    # =====================================================

    latest_risk_ids = (
        db.query(
            func.max(
                RiskScore.id
            ).label("latest_id")
        )
        .group_by(
            RiskScore.document_id
        )
        .subquery()
    )

    latest_risks = (
        db.query(RiskScore)
        .join(
            latest_risk_ids,
            RiskScore.id
            == latest_risk_ids.c.latest_id,
        )
        .all()
    )

    # =====================================================
    # 6. RISK DISTRIBUTION
    # =====================================================

    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for risk in latest_risks:

        level = (
            str(risk.risk_level).lower()
            if risk.risk_level
            else ""
        )

        if level in risk_distribution:
            risk_distribution[level] += 1

    # =====================================================
    # 7. AVERAGE RISK SCORE
    # =====================================================

    if latest_risks:

        risk_scores = [
            float(risk.risk_score)
            for risk in latest_risks
            if risk.risk_score is not None
        ]

        if risk_scores:
            average_risk_score = round(
                sum(risk_scores)
                / len(risk_scores),
                2,
            )
        else:
            average_risk_score = 0.0

    else:
        average_risk_score = 0.0

    # =====================================================
    # 8. OPEN ALERTS
    # =====================================================

    open_alerts = (
        db.query(
            func.count(Alert.id)
        )
        .filter(
            func.lower(Alert.status) == "open"
        )
        .scalar()
        or 0
    )

    # =====================================================
    # 9. TOTAL ALERTS
    # =====================================================

    total_alerts = (
        db.query(
            func.count(Alert.id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # 10. RESOLVED ALERTS
    # =====================================================

    resolved_alerts = (
        db.query(
            func.count(Alert.id)
        )
        .filter(
            func.lower(Alert.status)
            == "resolved"
        )
        .scalar()
        or 0
    )

    # =====================================================
    # 11. ALERT DISTRIBUTION
    # =====================================================

    alert_distribution = {
        "open": open_alerts,
        "resolved": resolved_alerts,
        "total": total_alerts,
    }

    # =====================================================
    # 12. HIGH + CRITICAL DOCUMENTS
    # =====================================================

    high_risk_documents = sum(
        1
        for risk in latest_risks
        if str(
            risk.risk_level
        ).lower()
        in {"high", "critical"}
    )

    # =====================================================
    # 13. CRITICAL DOCUMENTS
    # =====================================================

    critical_risk_documents = sum(
        1
        for risk in latest_risks
        if str(
            risk.risk_level
        ).lower()
        == "critical"
    )

    # =====================================================
    # 14. PROCESSING RATE
    # =====================================================

    if total_documents > 0:

        processing_rate = round(
            (
                analyzed_documents
                / total_documents
            ) * 100,
            2,
        )

    else:
        processing_rate = 0.0

    # =====================================================
    # 15. ANALYTICS STATUS
    # =====================================================

    if total_documents == 0:

        analytics_status = "no_data"

    elif analyzed_documents < total_documents:

        analytics_status = "partial"

    else:

        analytics_status = "active"

    # =====================================================
    # 16. RETURN ANALYTICS
    # =====================================================

    return {
        # Existing fields
        "total_documents": total_documents,
        "analyzed_documents": analyzed_documents,
        "similarity_comparisons": similarity_comparisons,
        "average_similarity": average_similarity,
        "risk_distribution": risk_distribution,
        "open_alerts": open_alerts,
        "high_risk_documents": high_risk_documents,
        "critical_risk_documents": (
            critical_risk_documents
        ),
        "processing_rate": processing_rate,

        # New analytics fields
        "average_risk_score": average_risk_score,

        "alert_distribution": alert_distribution,

        "analytics_status": analytics_status,
    }