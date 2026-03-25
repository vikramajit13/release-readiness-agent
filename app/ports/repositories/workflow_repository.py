from typing import Protocol

from app.domain.entities.workflow_run import WorkflowRun


class WorkflowRepository(Protocol):
    async def add(self, workflow_run: WorkflowRun) -> None:
        ...

    async def get_by_id(self, workflow_run_id: int) -> WorkflowRun | None:
        ...

    async def update(self, workflow_run: WorkflowRun) -> None:
        ...

    async def get_by_document_version_pk(self, document_version_pk: int) -> list[WorkflowRun]:
        ...