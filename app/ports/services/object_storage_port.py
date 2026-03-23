from typing import Protocol, BinaryIO


class ObjectStoragePort(Protocol):
    async def upload_bytes(self, key: str, content: bytes, content_type: str) -> str:
        return ""

    async def download_bytes(self, key: str) -> bytes:
        return ""
