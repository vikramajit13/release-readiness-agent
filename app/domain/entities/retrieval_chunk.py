from dataclasses import dataclass
from datetime import datetime


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_version_pk: int
    chunk_index: int
    chunk_text: str
    metadata_json: dict
    score: float