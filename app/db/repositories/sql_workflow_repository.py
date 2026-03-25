from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ports.repositories.workflow_repository import WorkflowRepository
from app.domain.entities.workflow_run import WorkflowRun
from app.db.models.workflow_run_model import WorkflowRunModel


class SqlWorkflowRepository(WorkflowRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, workflow_run: WorkflowRun) -> None:
        model = WorkflowRunModel(
            id=workflow_run.workflow_run_id,
            name=workflow_run.name,
            status=workflow_run.status,
            document_version_id=workflow_run.document_version_id,
            created_at=workflow_run.created_at,
            updated_at=workflow_run.updated_at,
            error_message=None,
        )
        self.session.add(model)

    async def get_by_id(self, workflow_run_id: int) -> WorkflowRun | None:
        stmt = select(WorkflowRunModel).where(WorkflowRunModel.id == workflow_run_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return WorkflowRun(
            workflow_run_id=model.id,
            name=model.name,
            status=model.status,
            document_version_id=model.document_version_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            error_message=model.error_message,
        )

    async def update(self, workflow_run: WorkflowRun) -> None:
        ...
        

    async def get_by_document_version_pk(
        self, document_version_pk: int
    ) -> list[WorkflowRun]: ...
