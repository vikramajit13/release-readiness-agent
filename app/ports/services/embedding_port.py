from typing import Protocol

class EmbeddingPort(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...