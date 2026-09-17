from typing import Any

from pydantic import BaseModel


class DocumentProcessingInfo(BaseModel):
    id: int
    file_name: str


class TextExtractionStatus(BaseModel):
    current_document: str
    compared_document: str


class NLPAnalysisStatus(BaseModel):
    current_document: str
    compared_document: str


class SimilarityProcessingResult(BaseModel):
    score: float
    method: str | None = None
    status: str


class RiskV1Result(BaseModel):
    id: int
    score: float
    level: str
    model: str


class RiskV2Result(BaseModel):
    id: int
    score: float
    level: str
    model: str
    features: dict[str, Any]


class AlertProcessingResult(BaseModel):
    id: int
    type: str
    severity: str
    status: str
    message: str | None = None


class ProcessingResponse(BaseModel):
    status: str

    document: DocumentProcessingInfo

    compared_document: DocumentProcessingInfo

    text_extraction: TextExtractionStatus

    nlp_analysis: NLPAnalysisStatus

    similarity: SimilarityProcessingResult

    risk_v1: RiskV1Result

    risk_v2: RiskV2Result

    alert: AlertProcessingResult