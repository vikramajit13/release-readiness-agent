from app.db.repositories.sql_document_repository import SqlDocumentRepository
from app.db.repositories.sql_workflow_repository import SqlWorkflowRepository
from app.db.session import AsyncSessionFactory
from app.db.repositories.sql_chunk_repository import SqlChunkRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory=AsyncSessionFactory):
        self.session_factory = session_factory
        self.session = None
        self.documents = None
        self.workflows = None
        self.chunks = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.documents = SqlDocumentRepository(self.session)
        self.workflows = SqlWorkflowRepository(self.session)
        self.chunks = SqlChunkRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()