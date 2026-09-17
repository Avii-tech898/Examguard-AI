from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Document, DocumentText, AnalysisResult
from backend.schemas import AnalysisResultResponse
from backend.services.nlp_analyzer import analyze_text


router = APIRouter(
    prefix="/api/documents",
    tags=["Analysis"]
)


@router.post(
    "/{document_id}/analyze",
    response_model=AnalysisResultResponse
)
def analyze_document(
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
    # 2. Get extracted document text
    # -------------------------------------------------
    document_text = (
        db.query(DocumentText)
        .filter(DocumentText.document_id == document_id)
        .first()
    )

    if not document_text:
        raise HTTPException(
            status_code=404,
            detail="Extracted text not found for this document"
        )

    # -------------------------------------------------
    # 3. Run NLP analysis
    # -------------------------------------------------
    analysis_data = analyze_text(
        document_text.extracted_text
    )

    # -------------------------------------------------
    # 4. Check for existing NLP analysis
    # -------------------------------------------------
    existing_result = (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.document_id == document_id,
            AnalysisResult.analysis_type == "nlp_basic"
        )
        .order_by(AnalysisResult.id.desc())
        .first()
    )

    # -------------------------------------------------
    # 5. Update existing result
    # -------------------------------------------------
    if existing_result:

        existing_result.result_data = analysis_data
        existing_result.model_version = "nlp-basic-v1"
        existing_result.confidence_score = 100.00

        analysis_result = existing_result

    # -------------------------------------------------
    # 6. Create new result if none exists
    # -------------------------------------------------
    else:

        analysis_result = AnalysisResult(
            document_id=document_id,
            analysis_type="nlp_basic",
            result_data=analysis_data,
            model_version="nlp-basic-v1",
            confidence_score=100.00
        )

        db.add(analysis_result)

    # -------------------------------------------------
    # 7. Save changes
    # -------------------------------------------------
    db.commit()
    db.refresh(analysis_result)

    return analysis_result


@router.get(
    "/{document_id}/analysis",
    response_model=AnalysisResultResponse
)
def get_document_analysis(
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
    # 2. Get latest analysis result
    # -------------------------------------------------
    analysis_result = (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.document_id == document_id
        )
        .order_by(AnalysisResult.id.desc())
        .first()
    )

    # -------------------------------------------------
    # 3. Check result
    # -------------------------------------------------
    if not analysis_result:
        raise HTTPException(
            status_code=404,
            detail="Analysis result not found for this document"
        )

    return analysis_result