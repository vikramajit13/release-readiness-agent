from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.entities.chunk import Chunk
from app.db.models.chunk_model import ChunkModel
from app.ports.repositories.chunk_repository import ChunkRepository
from app.domain.entities.retrieval_chunk import RetrievedChunk


class SqlChunkRepository(ChunkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_many(self, chunks: list[Chunk]) -> None:
        models = [
            ChunkModel(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_version_pk=chunk.document_version_pk,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                embedding=chunk.embedding,
                metadata_json=chunk.metadata_json,
                created_at=chunk.created_at,
            )
            for chunk in chunks
        ]
        self.session.add_all(models)

    async def search_hybrid(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:

        sql = text(
            """
            WITH vector_results AS (
                SELECT
                    id,
                    chunk_id,
                    document_id,
                    document_version_pk,
                    chunk_index,
                    chunk_text,
                    metadata_json,
                    ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:query_embedding AS vector)) AS vector_rank
                FROM chunks
                WHERE (:document_id IS NULL OR document_id = :document_id)
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :candidate_k
            ),
            lexical_results AS (
                SELECT
                    id,
                    chunk_id,
                    document_id,
                    document_version_pk,
                    chunk_index,
                    chunk_text,
                    metadata_json,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(chunk_text_tsv, websearch_to_tsquery('english', :query_text)) DESC
                    ) AS lexical_rank
                FROM chunks
                WHERE chunk_text_tsv @@ websearch_to_tsquery('english', :query_text)
                AND (:document_id IS NULL OR document_id = :document_id)
                ORDER BY ts_rank_cd(chunk_text_tsv, websearch_to_tsquery('english', :query_text)) DESC
                LIMIT :candidate_k
            )
            SELECT
                COALESCE(v.chunk_id, l.chunk_id) AS chunk_id,
                COALESCE(v.document_id, l.document_id) AS document_id,
                COALESCE(v.document_version_pk, l.document_version_pk) AS document_version_pk,
                COALESCE(v.chunk_index, l.chunk_index) AS chunk_index,
                COALESCE(v.chunk_text, l.chunk_text) AS chunk_text,
                COALESCE(v.metadata_json, l.metadata_json) AS metadata_json,
                v.vector_rank,
                l.lexical_rank,
                (
                    COALESCE(1.0 / (60 + v.vector_rank), 0.0) +
                    COALESCE(1.0 / (60 + l.lexical_rank), 0.0)
                ) AS score
            FROM vector_results v
            FULL OUTER JOIN lexical_results l ON v.id = l.id
            ORDER BY score DESC, chunk_index ASC
            LIMIT :top_k;
            """
        )
        
        # pgvector-python examples use passing embeddings directly into SQL parameters,
        # and cosine distance ordering is based on <=>. :contentReference[oaicite:1]{index=1}
        embedding_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"

        result = await self.session.execute(
            sql,
            {
                "query_text": query_text,
                "query_embedding": embedding_literal,
                "top_k": top_k,
                "candidate_k": candidate_k,
                "document_id": document_id,
            },
        )
        rows = result.mappings().all()

        return [
            RetrievedChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                document_version_pk=row["document_version_pk"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                metadata_json=row["metadata_json"],
                score=float(row["score"]),
                vector_rank=row["vector_rank"],
                lexical_rank=row["lexical_rank"],
            )
            for row in rows
        ]
