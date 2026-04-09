from app.ports.services.extractor_port import ExtractedDocument, ExtractorPort


class PlainTextExtractor(ExtractorPort):
    def supports(self, mime_type: str) -> bool:
        return mime_type in {"text/plain", "text/markdown"}

    async def extract(self, file_bytes: bytes, metadata: dict) -> ExtractedDocument:
        text = file_bytes.decode("utf-8")
        return ExtractedDocument(text=text, metadata=metadata)