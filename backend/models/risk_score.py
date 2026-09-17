from sqlalchemy import BigInteger, String, JSON, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    risk_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2),
        nullable=False
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    risk_factors: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[object | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )