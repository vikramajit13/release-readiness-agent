from pydantic import BaseModel, Field
from typing import Optional

class IngestTextRequest(BaseModel):
    content: str = Field(..., min_length=1)
    filename: Optional[str] = None
    content_type: str = "text/plain"
    external_id: Optional[str] = None

class IngestResponse(BaseModel):
    document_id: str
    version_id: str
    status: str