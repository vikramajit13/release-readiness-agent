import asyncio
from sentence_transformers import SentenceTransformer

from app.ports.services.embedding_port import EmbeddingPort


class SentenceTransformerAdapter(EmbeddingPort):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = await asyncio.to_thread(
            self.model.encode,
            texts,
            normalize_embeddings=True,
        )
        return [v.tolist() for v in vectors]