from dataclasses import dataclass
from datetime import datetime
from app.domain.enums.workflow_status import WorkflowStatus


@dataclass
class WorkflowRun:
    workflow_run_id: int | None
    name: str
    status: WorkflowStatus
    document_version_id: int
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None