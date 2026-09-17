from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RiskScoreBase(BaseModel):
    document_id: int
    risk_score: float
    risk_level: str
    risk_factors: dict[str, Any] | list[Any] | None = None
    model_version: str | None = None


class RiskScoreCreate(RiskScoreBase):
    pass


class RiskScoreResponse(RiskScoreBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)