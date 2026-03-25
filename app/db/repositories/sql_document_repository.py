from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.document import Document
from app.domain.entities.document_version import DocumentVersion
from app.db.models.document_model import DocumentModel
from app.db.models.document_version_model import DocumentVersionModel
from app.ports.repositories.document_repository import DocumentRepository


class SqlDocumentRepository(DocumentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, document: Document) -> None:
        model = DocumentModel(
            document_id=document.document_id,
            document_type=document.document_type,
            name=document.name,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        self.session.add(model)

    async def get_by_document_id(self, document_id: str) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return Document(
            document_id=model.document_id,
            document_type=model.document_type,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def update(self, document: Document) -> None:
        stmt = select(DocumentModel).where(DocumentModel.document_id == document.document_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Document not found: {document.document_id}")

        model.document_type = document.document_type
        model.name = document.name
        model.updated_at = document.updated_at

    async def add_version(self, document_version: DocumentVersion) -> None:
        model = DocumentVersionModel(
            document_version_id=document_version.document_version_id,
            document_pk=document_version.document_pk,
            version_number=document_version.version_number,
            storage_key=document_version.storage_key,
            mime_type=document_version.mime_type,
            created_at=document_version.created_at,
            updated_at=document_version.updated_at,
        )
        self.session.add(model)

    async def get_version_by_document_version_id(
        self,
        document_version_id: str,
    ) -> DocumentVersion | None:
        stmt = select(DocumentVersionModel).where(
            DocumentVersionModel.document_version_id == document_version_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return DocumentVersion(
            document_version_id=model.document_version_id,
            document_pk=model.document_pk,
            version_number=model.version_number,
            storage_key=model.storage_key,
            mime_type=model.mime_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_versions_by_document_pk(self, document_pk: int) -> list[DocumentVersion]:
        stmt = select(DocumentVersionModel).where(
            DocumentVersionModel.document_pk == document_pk
        ).order_by(DocumentVersionModel.version_number.asc())

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [
            DocumentVersion(
                document_version_id=model.document_version_id,
                document_pk=model.document_pk,
                version_number=model.version_number,
                storage_key=model.storage_key,
                mime_type=model.mime_type,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]