from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Document, RiskScore, Alert
from backend.schemas import AlertResponse
from backend.services.alert_engine import generate_alert


router = APIRouter(
    prefix="/api",
    tags=["Alerts"]
)


# =====================================================
# GET ALL ALERTS
# =====================================================

@router.get(
    "/alerts",
    response_model=list[AlertResponse]
)
def get_all_alerts(
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.id.desc())
        .all()
    )

    return alerts


# =====================================================
# CREATE / GENERATE ALERT
# =====================================================

@router.post(
    "/documents/{document_id}/alerts",
    response_model=AlertResponse
)
def create_document_alert(
    document_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Check document
    # -------------------------------------------------

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # -------------------------------------------------
    # 2. Get latest risk score
    # -------------------------------------------------

    risk_score = (
        db.query(RiskScore)
        .filter(
            RiskScore.document_id == document_id
        )
        .order_by(RiskScore.id.desc())
        .first()
    )

    if not risk_score:
        raise HTTPException(
            status_code=404,
            detail="Risk score not found for this document"
        )

    # -------------------------------------------------
    # 3. Generate alert data
    # -------------------------------------------------

    alert_data = generate_alert(
        risk_score=risk_score.risk_score,
        risk_level=risk_score.risk_level,
        risk_factors=risk_score.risk_factors
    )

    # -------------------------------------------------
    # 4. Check existing OPEN alert
    # -------------------------------------------------

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.document_id == document_id,
            Alert.risk_score_id == risk_score.id,
            Alert.status == "open"
        )
        .order_by(Alert.id.desc())
        .first()
    )

    # -------------------------------------------------
    # 5. Update existing OPEN alert
    # -------------------------------------------------

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

    # -------------------------------------------------
    # 6. Create new alert
    # -------------------------------------------------

    else:

        alert = Alert(
            document_id=document_id,
            risk_score_id=risk_score.id,
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            status=alert_data["status"],
            resolved_at=None
        )

        db.add(alert)

    # -------------------------------------------------
    # 7. Save
    # -------------------------------------------------

    db.commit()
    db.refresh(alert)

    return alert


# =====================================================
# GET LATEST ALERT FOR DOCUMENT
# =====================================================

@router.get(
    "/documents/{document_id}/alerts",
    response_model=AlertResponse
)
def get_document_alert(
    document_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Check document
    # -------------------------------------------------

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # -------------------------------------------------
    # 2. Get latest alert
    # -------------------------------------------------

    alert = (
        db.query(Alert)
        .filter(
            Alert.document_id == document_id
        )
        .order_by(Alert.id.desc())
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found for this document"
        )

    return alert


# =====================================================
# RESOLVE ALERT
# =====================================================

@router.patch(
    "/documents/{document_id}/alerts/{alert_id}/resolve",
    response_model=AlertResponse
)
def resolve_document_alert(
    document_id: int,
    alert_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Check document
    # -------------------------------------------------

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # -------------------------------------------------
    # 2. Find alert
    # -------------------------------------------------

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.document_id == document_id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found for this document"
        )

    # -------------------------------------------------
    # 3. Already resolved
    # -------------------------------------------------

    if alert.status == "resolved":
        return alert

    # -------------------------------------------------
    # 4. Resolve alert
    # -------------------------------------------------

    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)

    # -------------------------------------------------
    # 5. Save
    # -------------------------------------------------

    db.commit()
    db.refresh(alert)

    return alert
