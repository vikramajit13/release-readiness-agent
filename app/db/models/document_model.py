from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(
        String(75),
        unique=True,
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

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

    versions = relationship(
        "DocumentVersionModel",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"DocumentModel(id={self.id!r}, "
            f"document_id={self.document_id!r}, "
            f"document_type={self.document_type!r}, "
            f"name={self.name!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})"
        )