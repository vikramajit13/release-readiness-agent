from typing import Protocol

class ChunkRepository(Protocol):
    async def add_many(self, chunks: list) -> None:
        ...