from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SimilarityResultBase(BaseModel):
    document_id: int
    compared_document_id: int
    similarity_score: float | None = None
    similarity_method: str | None = None
    matching_sections: dict[str, Any] | list[Any] | None = None


class SimilarityResultCreate(SimilarityResultBase):
    pass


class SimilarityResultResponse(SimilarityResultBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)