from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Document, DocumentText
from backend.schemas import DocumentTextResponse
from backend.services.document_extractor import extract_text_from_pdf

from pathlib import Path

UPLOAD_DIR = Path("uploads/documents")

router = APIRouter(
    prefix="/api/documents",
    tags=["Document Text"]
)


@router.get("/{document_id}/text", response_model=DocumentTextResponse)
def get_document_text(
    document_id: int,
    db: Session = Depends(get_db)
):
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

    return document_text
@router.post("/{document_id}/extract-text", response_model=DocumentTextResponse)
def extract_document_text(
    document_id: int,
    db: Session = Depends(get_db)
):
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

    file_path = UPLOAD_DIR / document.file_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )

    try:
        extracted_text = extract_text_from_pdf(str(file_path))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(exc)}"
        )

    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from this document"
        )

    existing_text = (
        db.query(DocumentText)
        .filter(DocumentText.document_id == document_id)
        .first()
    )

    if existing_text:
        existing_text.extracted_text = extracted_text
        existing_text.ocr_engine = "pypdf"
        existing_text.ocr_confidence = 100.00
        existing_text.language = "en"
        document_text = existing_text
    else:
        document_text = DocumentText(
            document_id=document_id,
            extracted_text=extracted_text,
            ocr_engine="pypdf",
            ocr_confidence=100.00,
            language="en"
        )
        db.add(document_text)

    db.commit()
    db.refresh(document_text)

    return document_text