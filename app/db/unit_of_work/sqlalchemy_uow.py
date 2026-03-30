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


class IngestDocumentUseCase:
    def __init__(
        self,
        uow_factory,
        storage: ObjectStoragePort,
        queue: QueuePort,
        id_generator: IdGeneratorPort,
        clock: ClockPort,
    ):
        self.uow_factory = uow_factory
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
        _ = checksum  # keep for later when you add checksum to DocumentVersion

        document = Document(
            id=None,
            document_id=document_id,
            document_type=document_type,
            name=filename,
            created_at=now,
            updated_at=now,
        )

        async with self.uow_factory() as uow:
            await uow.documents.add(document)
            await uow.flush()

            persisted_document = await uow.documents.get_by_document_id(document_id)
            if persisted_document is None:
                raise ValueError(f"Document was not persisted: {document_id}")

            version = DocumentVersion(
                id=None,
                document_version_id=document_version_id,
                document_pk=persisted_document.id,
                version_number=1,
                storage_key=uploaded_storage_key,
                mime_type=content_type,
                created_at=now,
                updated_at=now,
            )

            await uow.documents.add_version(version)
            await uow.flush()

            persisted_version = await uow.documents.get_version_by_document_version_id(
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

            await uow.workflows.add(workflow)
            await uow.commit()

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