from pydantic import BaseModel

class IngestResponse(BaseModel):
    document_id: str
    version_id: str
    status: str