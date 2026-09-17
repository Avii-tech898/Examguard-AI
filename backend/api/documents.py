import hashlib
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import Document
from backend.schemas import DocumentResponse


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    file_content = file.file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    file_hash = hashlib.sha256(file_content).hexdigest()

    existing_document = (
        db.query(Document)
        .filter(Document.file_hash == file_hash)
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="This file has already been uploaded"
        )

    safe_filename = os.path.basename(file.filename)
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    document = Document(
        file_name=safe_filename,
        file_type=file.content_type,
        file_hash=file_hash,
        source_type="upload",
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db)
):
    documents = (
        db.query(Document)
        .order_by(Document.id.desc())
        .all()
    )

    return documents
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
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

    return document