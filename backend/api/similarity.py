from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Document, DocumentText, SimilarityResult
from backend.schemas import SimilarityResultResponse
from backend.services.similarity_engine import calculate_similarity


router = APIRouter(
    prefix="/api/documents",
    tags=["Similarity"]
)


@router.post(
    "/{document_id}/similarity/{compared_document_id}",
    response_model=SimilarityResultResponse
)
def calculate_document_similarity(
    document_id: int,
    compared_document_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Prevent self-comparison
    # -------------------------------------------------
    if document_id == compared_document_id:
        raise HTTPException(
            status_code=400,
            detail="A document cannot be compared with itself"
        )

    # -------------------------------------------------
    # 2. Check first document
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
    # 3. Check compared document
    # -------------------------------------------------
    compared_document = (
        db.query(Document)
        .filter(Document.id == compared_document_id)
        .first()
    )

    if not compared_document:
        raise HTTPException(
            status_code=404,
            detail="Compared document not found"
        )

    # -------------------------------------------------
    # 4. Get text of first document
    # -------------------------------------------------
    document_text = (
        db.query(DocumentText)
        .filter(
            DocumentText.document_id == document_id
        )
        .first()
    )

    if not document_text:
        raise HTTPException(
            status_code=404,
            detail="Extracted text not found for document"
        )

    # -------------------------------------------------
    # 5. Get text of compared document
    # -------------------------------------------------
    compared_document_text = (
        db.query(DocumentText)
        .filter(
            DocumentText.document_id == compared_document_id
        )
        .first()
    )

    if not compared_document_text:
        raise HTTPException(
            status_code=404,
            detail="Extracted text not found for compared document"
        )

    # -------------------------------------------------
    # 6. Calculate similarity
    # -------------------------------------------------
    similarity_score = calculate_similarity(
        document_text.extracted_text,
        compared_document_text.extracted_text
    )

    # -------------------------------------------------
    # 7. Check existing similarity result
    # -------------------------------------------------
    existing_result = (
        db.query(SimilarityResult)
        .filter(
            SimilarityResult.document_id == document_id,
            SimilarityResult.compared_document_id == compared_document_id
        )
        .order_by(SimilarityResult.id.desc())
        .first()
    )

    # -------------------------------------------------
    # 8. Update existing result
    # -------------------------------------------------
    if existing_result:

        existing_result.similarity_score = similarity_score
        existing_result.similarity_method = "tfidf_cosine"

        similarity_result = existing_result

    # -------------------------------------------------
    # 9. Create new result
    # -------------------------------------------------
    else:

        similarity_result = SimilarityResult(
            document_id=document_id,
            compared_document_id=compared_document_id,
            similarity_score=similarity_score,
            similarity_method="tfidf_cosine"
        )

        db.add(similarity_result)

    # -------------------------------------------------
    # 10. Save
    # -------------------------------------------------
    db.commit()
    db.refresh(similarity_result)

    return similarity_result


@router.get(
    "/{document_id}/similarity/{compared_document_id}",
    response_model=SimilarityResultResponse
)
def get_similarity_result(
    document_id: int,
    compared_document_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Prevent self-comparison
    # -------------------------------------------------
    if document_id == compared_document_id:
        raise HTTPException(
            status_code=400,
            detail="A document cannot be compared with itself"
        )

    # -------------------------------------------------
    # 2. Check first document
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
    # 3. Check compared document
    # -------------------------------------------------
    compared_document = (
        db.query(Document)
        .filter(Document.id == compared_document_id)
        .first()
    )

    if not compared_document:
        raise HTTPException(
            status_code=404,
            detail="Compared document not found"
        )

    # -------------------------------------------------
    # 4. Get latest similarity result
    # -------------------------------------------------
    similarity_result = (
        db.query(SimilarityResult)
        .filter(
            SimilarityResult.document_id == document_id,
            SimilarityResult.compared_document_id == compared_document_id
        )
        .order_by(SimilarityResult.id.desc())
        .first()
    )

    if not similarity_result:
        raise HTTPException(
            status_code=404,
            detail="Similarity result not found"
        )

    return similarity_result