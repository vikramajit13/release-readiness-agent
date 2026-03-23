from typing import Protocol
from .repositories.chunk_repository import ChunkRepository
from .repositories.document_repository import DocumentRepository
from .repositories.workflow_repository import WorkflowRepository


class UnitOfWork(Protocol):
    documents: DocumentRepository
    workflows: WorkflowRepository
    chunks: ChunkRepository

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc, tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
