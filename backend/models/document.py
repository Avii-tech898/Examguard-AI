from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    file_hash: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        nullable=True
    )

    source_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    exam_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    exam_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        server_default=text("'uploaded'")
    )

    uploaded_at: Mapped[object | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )