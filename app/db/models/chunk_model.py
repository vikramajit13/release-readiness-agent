from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String(75), unique=True, nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(75), nullable=False, index=True)
    document_version_pk: Mapped[int] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=False)  # replace with pgvector later
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )