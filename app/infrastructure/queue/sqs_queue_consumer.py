from __future__ import annotations

import asyncio
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError


class SqsConsumerError(Exception):
    pass


class SqsQueueConsumer:
    def __init__(
        self,
        *,
        queue_url: str,
        region_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.queue_url = queue_url

        session_kwargs: dict = {"region_name": region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token:
            session_kwargs["aws_session_token"] = aws_session_token

        session = boto3.session.Session(**session_kwargs)
        self.client = session.client("sqs", endpoint_url=endpoint_url)

    async def receive_messages(self, max_messages: int = 1) -> list[dict]:
        try:
            response = await asyncio.to_thread(
                self.client.receive_message,
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,
                MessageAttributeNames=["All"],
            )
            return response.get("Messages", [])
        except (ClientError, BotoCoreError) as exc:
            raise SqsConsumerError("Failed to receive messages from SQS") from exc

    async def delete_message(self, receipt_handle: str) -> None:
        try:
            await asyncio.to_thread(
                self.client.delete_message,
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
        except (ClientError, BotoCoreError) as exc:
            raise SqsConsumerError("Failed to delete SQS message") from exc

    @staticmethod
    def parse_body(message: dict) -> dict:
        return json.loads(message["Body"])