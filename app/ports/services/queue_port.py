from typing import Protocol

class QueuePort(Protocol):
    async def publish(self, payload: dict) -> None:
        ...
        
    