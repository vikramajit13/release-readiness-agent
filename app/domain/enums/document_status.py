from enum import Enum


class DocumentStatus(str, Enum):
    RECEIVED = "RECEIVED"
    STORED = "STORED"
    QUEUED = "QUEUED"
    PROCESESSING = "PROCESSING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
