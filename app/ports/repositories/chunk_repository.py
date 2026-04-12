from typing import Protocol
from app.domain.entities.chunk import Chunk
from app.domain.entities.retrieval_chunk import RetrievedChunk


class ChunkRepository(Protocol):
    async def add_many_from_worker(
        self,
        chunks: list[Chunk]
    ) -> None:
        ...
    
    async def search_hybrid(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        ...