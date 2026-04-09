from typing import Protocol


class ChunkRepository(Protocol):
    async def add_many_from_worker(
        self,
        document_id: str,
        document_version_id: int,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        ...