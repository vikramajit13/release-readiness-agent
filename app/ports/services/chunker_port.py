from typing import Protocol

class ChunkInput:
    def __init__(self, text: str, metadata: dict):
        self.text = text
        self.metadata = metadata

class ChunkResult:
    def __init__(self, chunk_index: int, text: str, metadata: dict):
        self.chunk_index = chunk_index
        self.text = text
        self.metadata = metadata

class ChunkerPort(Protocol):
    async def chunk(self, chunk_input: ChunkInput) -> list[ChunkResult]:
        ...