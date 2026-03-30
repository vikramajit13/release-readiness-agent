import hashlib

from app.application.dto.ingest_response import IngestResponse
from app.domain.entities.document import Document
from app.domain.entities.document_version import DocumentVersion
from app.domain.entities.workflow_run import WorkflowRun
from app.domain.enums.workflow_status import WorkflowStatus
from app.ports.services.clock_port import ClockPort
from app.ports.services.id_generator_port import IdGeneratorPort
from app.ports.services.object_storage_port import ObjectStoragePort
from app.ports.services.queue_port import QueuePort
from app.db.unit_of_work.uow_factory import UOW_factory


class IngestDocumentUseCase:
    def __init__(
        self,
        uow_factory: UOW_factory,
        storage: ObjectStoragePort,
        queue: QueuePort,
        id_generator: IdGeneratorPort,
        clock: ClockPort,
    ):
        self.uow = uow_factory
        self.storage = storage
        self.queue = queue
        self.id_generator = id_generator
        self.clock = clock

    async def execute(
        self,
        *,
        filename: str,
        content_bytes: bytes,
        content_type: str,
        document_type: str,
    ) -> IngestResponse:
        now = self.clock.utcnow()

        document_id = self.id_generator.new_id("doc")
        document_version_id = self.id_generator.new_id("ver")

        storage_key = f"documents/{document_id}/{document_version_id}/{filename}"
        uploaded_storage_key = await self.storage.upload_bytes(
            key=storage_key,
            content=content_bytes,
            content_type=content_type,
        )

        checksum = hashlib.sha256(content_bytes).hexdigest()

        document = Document(
            document_id=document_id,
            document_type=document_type,
            name=filename,
            created_at=now,
            updated_at=now,
        )

        async with self.uow:
            await self.uow.documents.add(document)

            # We need the DB-generated PK of the inserted document row.
            await self.uow.flush()

            persisted_document = await self.uow.documents.get_by_document_id(document_id)
            if persisted_document is None:
                raise ValueError(f"Document was not persisted: {document_id}")

            # This assumes your Document domain entity includes internal DB pk.
            # If not, your repository contract needs adjusting.
            version = DocumentVersion(
                document_version_id=document_version_id,
                document_pk=persisted_document.id,
                version_number=1,
                storage_key=uploaded_storage_key,
                mime_type=content_type,
                created_at=now,
                updated_at=now,
            )

            await self.uow.documents.add_version(version)
            await self.uow.flush()

            persisted_version = await self.uow.documents.get_version_by_document_version_id(
                document_version_id
            )
            if persisted_version is None:
                raise ValueError(f"Document version was not persisted: {document_version_id}")

            workflow = WorkflowRun(
                workflow_run_id=None,
                name="INGEST_DOCUMENT",
                status=WorkflowStatus.PENDING,
                document_version_id=persisted_version.id,
                created_at=now,
                updated_at=now,
                error_message=None,
            )

            await self.uow.workflows.add(workflow)
            await self.uow.commit()

        await self.queue.publish(
            {
                "event_type": "document.ingest.requested",
                "document_id": document_id,
                "document_version_id": document_version_id,
                "storage_key": uploaded_storage_key,
                "content_type": content_type,
            }
        )

        return IngestResponse(
            document_id=document_id,
            version_id=document_version_id,
            status="QUEUED",
        )