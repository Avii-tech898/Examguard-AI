from sqlalchemy import BigInteger, String, JSON, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    analysis_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    result_data: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    confidence_score: Mapped[float | None] = mapped_column(
        DECIMAL(5, 2),
        nullable=True
    )

    created_at: Mapped[object | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )