from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    document_id: str
    document_type: str
    name: str
    created_at: datetime
    updated_at: datetime