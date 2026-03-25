from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.enums.workflow_status import WorkflowStatus
from .base import Base


class WorkflowRunModel(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus, name="workflow_status_enum"),
        nullable=False,
        default=WorkflowStatus.PENDING,
        server_default=WorkflowStatus.PENDING.value,
    )

    document_version_id: Mapped[int] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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

    document_version = relationship(
        "DocumentVersionModel",
        back_populates="workflow_runs",
    )

    def __repr__(self) -> str:
        return (
            f"WorkflowRunModel(id={self.id!r}, "
            f"name={self.name!r}, "
            f"status={self.status!r}, "
            f"document_version_id={self.document_version_id!r}, "
            f"error_message={self.error_message!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})"
        )