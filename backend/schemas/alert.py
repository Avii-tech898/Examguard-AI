from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    document_id: int
    risk_score_id: int | None = None
    alert_type: str
    severity: str
    message: str | None = None
    status: str | None = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    created_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)