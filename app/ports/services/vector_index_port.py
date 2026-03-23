from typing import Protocol

class VectorRecord:
    def __init__(self, chunk_id: str, document_id: str, version_id: str, text: str, embedding: list[float], metadata: dict):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.version_id = version_id
        self.text = text
        self.embedding = embedding
        self.metadata = metadata

class VectorIndexPort(Protocol):
    async def index_records(self, records: list[VectorRecord]) -> None:
        ...