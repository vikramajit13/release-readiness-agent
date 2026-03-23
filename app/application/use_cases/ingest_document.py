class IngestDocumentUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        storage: ObjectStoragePort,
        queue: QueuePort,
        id_generator,
        clock,
    ):
        self.uow = uow
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
        external_id: str | None = None,
    ) -> IngestResponse:
        document_id = self.id_generator.new_id("doc")
        version_id = self.id_generator.new_id("ver")
        workflow_run_id = self.id_generator.new_id("wf")

        storage_key = f"documents/{document_id}/{version_id}/{filename}"
        storage_uri = await self.storage.upload_bytes(
            key=storage_key,
            content=content_bytes,
            content_type=content_type,
        )

        document = Document.create(
            document_id=document_id,
            external_id=external_id,
            created_at=self.clock.utcnow(),
        )

        version = DocumentVersion.create(
            version_id=version_id,
            document_id=document_id,
            storage_uri=storage_uri,
            mime_type=content_type,
            checksum="compute-me",
            file_size_bytes=len(content_bytes),
            created_at=self.clock.utcnow(),
        )

        workflow = WorkflowRun.create_ingestion_run(
            workflow_run_id=workflow_run_id,
            document_id=document_id,
            version_id=version_id,
            created_at=self.clock.utcnow(),
        )

        async with self.uow:
            await self.uow.documents.add(document)
            await self.uow.documents.add_version(version)
            await self.uow.workflows.add(workflow)
            await self.uow.commit()

        await self.queue.publish(
            topic="document.ingest.requested",
            payload={
                "document_id": document_id,
                "version_id": version_id,
                "workflow_run_id": workflow_run_id,
            },
        )

        return IngestResponse(
            document_id=document_id,
            version_id=version_id,
            status="QUEUED",
        )