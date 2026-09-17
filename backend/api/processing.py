from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.processing import (
    ProcessingResponse,
)
from backend.services.processing_engine import (
    process_document_pair,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Processing"],
)


@router.post(
    "/{document_id}/process/{compared_document_id}",
    response_model=ProcessingResponse,
)
def process_document(
    document_id: int,
    compared_document_id: int,
    db: Session = Depends(get_db),
):
    try:

        result = process_document_pair(
            document_id=document_id,
            compared_document_id=compared_document_id,
            db=db,
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Processing pipeline failed: {exc}",
        )