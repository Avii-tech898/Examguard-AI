from sqlalchemy import BigInteger, String, Text, DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class DocumentText(Base):
    __tablename__ = "document_text"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    ocr_engine: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    ocr_confidence: Mapped[float | None] = mapped_column(
        DECIMAL(5, 2),
        nullable=True
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[object | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )