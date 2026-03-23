from typing import Protocol

class QueuePort(Protocol):
    async def publish(self, topic: str, payload: dict) -> None:
        print("publish")
        
    