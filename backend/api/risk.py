from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import (
    Document,
    SimilarityResult,
    RiskScore,
    AnalysisResult,
)
from backend.schemas import RiskScoreResponse

from backend.services.risk_engine import (
    calculate_risk,
    calculate_feature_based_risk,
)

from backend.services.feature_engine import (
    build_document_features,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Risk"]
)


# =====================================================
# HELPER - CHECK DOCUMENT
# =====================================================

def get_document(
    document_id: int,
    db: Session
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# =====================================================
# HELPER - GET SIMILARITY RESULT
# =====================================================

def get_similarity_result(
    document_id: int,
    compared_document_id: int,
    db: Session
):
    """
    Get latest similarity result for a document pair.

    First checks:

        document_id -> compared_document_id

    Then checks reverse:

        compared_document_id -> document_id
    """

    similarity_result = (
        db.query(SimilarityResult)
        .filter(
            SimilarityResult.document_id == document_id,
            SimilarityResult.compared_document_id
            == compared_document_id
        )
        .order_by(
            SimilarityResult.id.desc()
        )
        .first()
    )

    if not similarity_result:

        similarity_result = (
            db.query(SimilarityResult)
            .filter(
                SimilarityResult.document_id
                == compared_document_id,
                SimilarityResult.compared_document_id
                == document_id
            )
            .order_by(
                SimilarityResult.id.desc()
            )
            .first()
        )

    return similarity_result


# =====================================================
# HELPER - GET LATEST NLP ANALYSIS
# =====================================================

def get_latest_analysis(
    document_id: int,
    db: Session
):
    """
    Get latest NLP analysis for a document.
    """

    return (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.document_id
            == document_id
        )
        .order_by(
            AnalysisResult.id.desc()
        )
        .first()
    )


# =====================================================
# HELPER - SAVE / UPDATE VERSIONED RISK
# =====================================================

def save_versioned_risk(
    document_id: int,
    risk_data: dict,
    risk_factors,
    db: Session
):
    """
    Save risk result separately for each model version.

    V1:
        risk-rule-v1

    V2:
        risk-rule-v2

    IMPORTANT:
    V1 and V2 are stored independently.
    """

    model_version = risk_data["model_version"]

    existing_risk = (
        db.query(RiskScore)
        .filter(
            RiskScore.document_id == document_id,
            RiskScore.model_version == model_version
        )
        .order_by(
            RiskScore.id.desc()
        )
        .first()
    )

    # -------------------------------------------------
    # UPDATE EXISTING VERSION
    # -------------------------------------------------

    if existing_risk:

        existing_risk.risk_score = (
            risk_data["risk_score"]
        )

        existing_risk.risk_level = (
            risk_data["risk_level"]
        )

        existing_risk.risk_factors = (
            risk_factors
        )

        existing_risk.model_version = (
            model_version
        )

        risk_score = existing_risk

    # -------------------------------------------------
    # CREATE NEW VERSION
    # -------------------------------------------------

    else:

        risk_score = RiskScore(
            document_id=document_id,
            risk_score=risk_data["risk_score"],
            risk_level=risk_data["risk_level"],
            risk_factors=risk_factors,
            model_version=model_version
        )

        db.add(risk_score)

    db.commit()
    db.refresh(risk_score)

    return risk_score


# =====================================================
# V1 - BASELINE RISK ENGINE
# =====================================================

@router.post(
    "/{document_id}/risk/{compared_document_id}",
    response_model=RiskScoreResponse
)
def calculate_document_risk(
    document_id: int,
    compared_document_id: int,
    db: Session = Depends(get_db)
):
    """
    Risk Engine V1.

    Baseline similarity-based risk model.

    Model:
        risk-rule-v1

    IMPORTANT:
        V1 result is stored separately from V2.
    """

    # -------------------------------------------------
    # 1. Prevent self-comparison
    # -------------------------------------------------

    if document_id == compared_document_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "A document cannot be compared "
                "with itself"
            )
        )

    # -------------------------------------------------
    # 2. Check documents
    # -------------------------------------------------

    get_document(
        document_id,
        db
    )

    get_document(
        compared_document_id,
        db
    )

    # -------------------------------------------------
    # 3. Get similarity
    # -------------------------------------------------

    similarity_result = get_similarity_result(
        document_id,
        compared_document_id,
        db
    )

    if not similarity_result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Similarity result not found for "
                "this document pair. "
                "Calculate similarity first."
            )
        )

    # -------------------------------------------------
    # 4. Calculate V1 risk
    # -------------------------------------------------

    risk_data = calculate_risk(
        float(similarity_result.similarity_score)
    )

    # -------------------------------------------------
    # 5. Force V1 model version
    # -------------------------------------------------

    risk_data["model_version"] = "risk-rule-v1"

    # -------------------------------------------------
    # 6. Save V1 independently
    # -------------------------------------------------

    risk_score = save_versioned_risk(
        document_id=document_id,
        risk_data=risk_data,
        risk_factors=risk_data["risk_factors"],
        db=db
    )

    return risk_score


# =====================================================
# V2 - ENHANCED FEATURE-BASED RISK ENGINE
# =====================================================

@router.post(
    "/{document_id}/risk-v2/{compared_document_id}",
    response_model=RiskScoreResponse
)
def calculate_document_risk_v2(
    document_id: int,
    compared_document_id: int,
    db: Session = Depends(get_db)
):
    """
    Risk Engine V2.

    Enhanced feature-based risk model.

    Features:

    - TF-IDF similarity
    - Word count difference
    - Sentence count difference
    - Character count difference
    - Unique word difference
    - Text density

    Model:
        risk-rule-v2

    IMPORTANT:
        V2 result is stored separately from V1.
    """

    # -------------------------------------------------
    # 1. Prevent self-comparison
    # -------------------------------------------------

    if document_id == compared_document_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "A document cannot be compared "
                "with itself"
            )
        )

    # -------------------------------------------------
    # 2. Check documents
    # -------------------------------------------------

    get_document(
        document_id,
        db
    )

    get_document(
        compared_document_id,
        db
    )

    # -------------------------------------------------
    # 3. Get similarity
    # -------------------------------------------------

    similarity_result = get_similarity_result(
        document_id,
        compared_document_id,
        db
    )

    if not similarity_result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Similarity result not found for "
                "this document pair. "
                "Calculate similarity first."
            )
        )

    # -------------------------------------------------
    # 4. Get current document NLP analysis
    # -------------------------------------------------

    current_analysis = get_latest_analysis(
        document_id,
        db
    )

    if not current_analysis:

        raise HTTPException(
            status_code=404,
            detail=(
                "NLP analysis not found for "
                f"document {document_id}. "
                "Generate analysis first."
            )
        )

    # -------------------------------------------------
    # 5. Get compared document NLP analysis
    # -------------------------------------------------

    compared_analysis = get_latest_analysis(
        compared_document_id,
        db
    )

    if not compared_analysis:

        raise HTTPException(
            status_code=404,
            detail=(
                "NLP analysis not found for "
                f"document {compared_document_id}. "
                "Generate analysis first."
            )
        )

    # -------------------------------------------------
    # 6. Build feature vector
    # -------------------------------------------------

    features = build_document_features(
        current_analysis={
            "result_data":
                current_analysis.result_data
        },
        compared_analysis={
            "result_data":
                compared_analysis.result_data
        },
        similarity_score=float(
            similarity_result.similarity_score
        )
    )

    # -------------------------------------------------
    # 7. Calculate V2 risk
    # -------------------------------------------------

    risk_data = calculate_feature_based_risk(
        features
    )

    # -------------------------------------------------
    # 8. Force V2 model version
    # -------------------------------------------------

    risk_data["model_version"] = "risk-rule-v2"

    # -------------------------------------------------
    # 9. Prepare risk factors
    # -------------------------------------------------

    risk_factors = list(
        risk_data["risk_factors"]
    )

    # Add feature snapshot

    risk_factors.append(
        {
            "feature_snapshot": features
        }
    )

    # -------------------------------------------------
    # 10. Save V2 independently
    # -------------------------------------------------

    risk_score = save_versioned_risk(
        document_id=document_id,
        risk_data=risk_data,
        risk_factors=risk_factors,
        db=db
    )

    return risk_score


# =====================================================
# GET LATEST RISK
# =====================================================

@router.get(
    "/{document_id}/risk",
    response_model=RiskScoreResponse
)
def get_document_risk(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get latest risk result.

    Usually V2 will be returned if V2
    has been generated most recently.
    """

    get_document(
        document_id,
        db
    )

    risk_score = (
        db.query(RiskScore)
        .filter(
            RiskScore.document_id
            == document_id
        )
        .order_by(
            RiskScore.id.desc()
        )
        .first()
    )

    if not risk_score:

        raise HTTPException(
            status_code=404,
            detail=(
                "Risk score not found for "
                "this document"
            )
        )

    return risk_score


# =====================================================
# GET V1 RISK
# =====================================================

@router.get(
    "/{document_id}/risk-v1",
    response_model=RiskScoreResponse
)
def get_document_risk_v1(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Risk Engine V1 result only.
    """

    get_document(
        document_id,
        db
    )

    risk_score = (
        db.query(RiskScore)
        .filter(
            RiskScore.document_id == document_id,
            RiskScore.model_version == "risk-rule-v1"
        )
        .order_by(
            RiskScore.id.desc()
        )
        .first()
    )

    if not risk_score:

        raise HTTPException(
            status_code=404,
            detail=(
                "V1 risk assessment has not "
                "been generated for this document."
            )
        )

    return risk_score


# =====================================================
# GET V2 RISK
# =====================================================

@router.get(
    "/{document_id}/risk-v2",
    response_model=RiskScoreResponse
)
def get_document_risk_v2(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Risk Engine V2 result only.
    """

    get_document(
        document_id,
        db
    )

    risk_score = (
        db.query(RiskScore)
        .filter(
            RiskScore.document_id == document_id,
            RiskScore.model_version == "risk-rule-v2"
        )
        .order_by(
            RiskScore.id.desc()
        )
        .first()
    )

    if not risk_score:

        raise HTTPException(
            status_code=404,
            detail=(
                "V2 risk assessment has not "
                "been generated for this document."
            )
        )

    return risk_score