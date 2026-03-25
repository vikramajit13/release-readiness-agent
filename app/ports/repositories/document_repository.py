from typing import Protocol

from app.domain.entities.document import Document
from app.domain.entities.document_version import DocumentVersion


class DocumentRepository(Protocol):
    async def add(self, document: Document) -> None:
        ...

    async def get_by_document_id(self, document_id: str) -> Document | None:
        ...

    async def update(self, document: Document) -> None:
        ...

    async def add_version(self, document_version: DocumentVersion) -> None:
        ...

    async def get_version_by_document_version_id(
        self, document_version_id: str
    ) -> DocumentVersion | None:
        ...

    async def get_versions_by_document_pk(self, document_pk: int) -> list[DocumentVersion]:
        ...