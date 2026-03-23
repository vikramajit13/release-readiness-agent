from typing import Protocol


class ExtractedDocument:
    def __init__(self, text: str, metadata: dict, pages: list[dict] | None = None):
        self.text = text
        self.metadata = metadata
        self.pages = pages or []


class ExtractorPort(Protocol):
    def supports(self, mime_type: str) -> bool: ...

    async def extract(self, file_bytes: bytes, metadata: dict) -> ExtractedDocument: ...
