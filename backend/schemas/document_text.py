from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentTextBase(BaseModel):
    document_id: int
    extracted_text: str | None = None
    ocr_engine: str | None = None
    ocr_confidence: float | None = None
    language: str | None = None


class DocumentTextCreate(DocumentTextBase):
    pass


class DocumentTextResponse(DocumentTextBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
