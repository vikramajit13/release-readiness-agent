from app.domain.enums.workflow_status import WorkflowStatus


class IngestDocumentHandler:
    def __init__(
        self,
        uow_factory,
        storage,
        extractor_factory,
        chunker,
        embedder,
        chunk_repository_factory=None,  # optional if chunks live under uow later
        clock=None,
    ):
        self.uow_factory = uow_factory
        self.storage = storage
        self.extractor_factory = extractor_factory
        self.chunker = chunker
        self.embedder = embedder
        self.clock = clock

    async def handle(self, payload: dict) -> None:
        document_id = payload["document_id"]
        document_version_id = payload["document_version_id"]
        storage_key = payload["storage_key"]
        content_type = payload["content_type"]

        async with self.uow_factory() as uow:
            document = await uow.documents.get_by_document_id(document_id)
            version = await uow.documents.get_version_by_document_version_id(document_version_id)

            if document is None or version is None:
                raise ValueError("Document or version not found")

            workflow_runs = await uow.workflows.get_by_document_version_pk(version.id)
            if not workflow_runs:
                raise ValueError("Workflow run not found")

            workflow = workflow_runs[-1]
            workflow.status = WorkflowStatus.RUNNING
            workflow.updated_at = self.clock.utcnow()
            await uow.workflows.update(workflow)
            await uow.commit()

        file_bytes = await self.storage.download_bytes(storage_key)

        extractor = self.extractor_factory.for_mime_type(content_type)
        extracted = await extractor.extract(file_bytes, {"document_id": document_id})

        chunks = await self.chunker.chunk_text(
            text=extracted.text,
            metadata={
                "document_id": document_id,
                "document_version_id": document_version_id,
                "mime_type": content_type,
            },
        )

        embeddings = await self.embedder.embed_texts([c["text"] for c in chunks])

        async with self.uow_factory() as uow:
            version = await uow.documents.get_version_by_document_version_id(document_version_id)
            workflow_runs = await uow.workflows.get_by_document_version_pk(version.id)
            workflow = workflow_runs[-1]

            await uow.chunks.add_many_from_worker(
                document_id=document_id,
                document_version_id=version.id,
                chunks=chunks,
                embeddings=embeddings,
            )

            workflow.status = WorkflowStatus.SUCCEEDED
            workflow.updated_at = self.clock.utcnow()
            await uow.workflows.update(workflow)
            await uow.commit()