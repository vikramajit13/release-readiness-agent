from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DocumentVersionModel(Base):
    __tablename__ = "document_versions"

    __table_args__ = (
        UniqueConstraint("document_pk", "version_number", name="uq_document_version_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    document_version_id: Mapped[str] = mapped_column(
        String(75),
        unique=True,
        nullable=False,
        index=True,
    )

    document_pk: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    document = relationship(
        "DocumentModel",
        back_populates="versions",
    )

    workflow_runs = relationship(
        "WorkflowRunModel",
        back_populates="document_version",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"DocumentVersionModel(id={self.id!r}, "
            f"document_version_id={self.document_version_id!r}, "
            f"document_pk={self.document_pk!r}, "
            f"version_number={self.version_number!r}, "
            f"storage_key={self.storage_key!r}, "
            f"mime_type={self.mime_type!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})"
        )