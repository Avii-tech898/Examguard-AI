from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    file_name: str
    file_type: str | None = None
    file_hash: str | None = None
    source_type: str | None = None
    exam_name: str | None = None
    exam_year: int | None = None
    status: str | None = "uploaded"


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)