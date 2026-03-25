from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentVersion:
    document_version_id: int
    document_id: int
    version_number: int
    storage_key: str
    mime_type: str
    created_at: datetime
    updated_at: datetime