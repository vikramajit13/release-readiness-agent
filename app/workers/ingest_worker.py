import asyncio

from app.infrastructure.queue.sqs_queue_consumer import SqsQueueConsumer
from app.workers.handlers.ingest_document_handler import IngestDocumentHandler


class IngestWorker:
    def __init__(
        self,
        consumer: SqsQueueConsumer,
        handler: IngestDocumentHandler,
    ) -> None:
        self.consumer = consumer
        self.handler = handler

    async def run_forever(self) -> None:
        while True:
            messages = await self.consumer.receive_messages(max_messages=1)

            if not messages:
                continue

            for message in messages:
                receipt_handle = message["ReceiptHandle"]
                payload = self.consumer.parse_body(message)

                try:
                    await self.handler.handle(payload)
                    await self.consumer.delete_message(receipt_handle)
                except Exception:
                    # log properly later
                    continue