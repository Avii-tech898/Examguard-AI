from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalysisResultBase(BaseModel):
    document_id: int
    analysis_type: str
    result_data: dict[str, Any] | list[Any] | None = None
    model_version: str | None = None
    confidence_score: float | None = None


class AnalysisResultCreate(AnalysisResultBase):
    pass


class AnalysisResultResponse(AnalysisResultBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)