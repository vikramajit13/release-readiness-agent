from app.db.repositories.sql_document_repository import SqlDocumentRepository
from app.db.repositories.sql_workflow_repository import SqlWorkflowRepository
from app.db.session import AsyncSessionFactory


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory = AsyncSessionFactory):
        self.session_factory = session_factory
        self.session = None
        self.documents = None
        self.workflows = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.documents = SqlDocumentRepository(self.session)
        self.workflows = SqlWorkflowRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
    
    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self):
        await self.session.rollback()