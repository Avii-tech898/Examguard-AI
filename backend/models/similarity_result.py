from sqlalchemy import BigInteger, String, JSON, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class SimilarityResult(Base):
    __tablename__ = "similarity_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    compared_document_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    similarity_score: Mapped[float | None] = mapped_column(
        DECIMAL(6, 3),
        nullable=True
    )

    similarity_method: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    matching_sections: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[object | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )