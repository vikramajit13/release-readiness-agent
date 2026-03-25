from __future__ import annotations

import asyncio
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.ports.services.queue_port import QueuePort


class SqsQueueError(Exception):
    pass


class SqsQueueAdapter(QueuePort):
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

        self.client = session.client(
            "sqs",
            endpoint_url=endpoint_url,
        )

    async def publish(self, payload: dict) -> None:
        try:
            message_body = json.dumps(payload)

            await asyncio.to_thread(
                self.client.send_message,
                QueueUrl=self.queue_url,
                MessageBody=message_body,
            )
        except (ClientError, BotoCoreError, TypeError, ValueError) as exc:
            raise SqsQueueError("Failed to publish message to SQS") from exc