from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from app.application.use_cases.ingest_document import IngestDocumentUseCase
from app.api.dependencies import get_ingest_document_use_case


router = APIRouter()

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    file: UploadFile = File(...),
    use_case: IngestDocumentUseCase = Depends(get_ingest_document_use_case),
):
    content = await file.read()
    
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    
    result = await use_case.execute(
        filename=file.filename or "uploaded.bin",
        content_bytes=content,
        content_type=file.content_type or "application/octet-stream",
        document_type="file",
    )
    return result
    
    