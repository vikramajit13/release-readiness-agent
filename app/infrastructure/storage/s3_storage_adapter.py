from __future__ import annotations

import asyncio
import boto3
#from botocore.exceptions import BotoCoreError, ClientError


from app.ports.services.object_storage_port import ObjectStoragePort


class S3StorageError(Exception):
    pass


class S3StorageAdapter(ObjectStoragePort):
    def __init__(
        self,
        *,
        bucket_name: str,
        region_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        
        self.bucket_name = bucket_name

        session_kwargs: dict = {"region_name": region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token:
            session_kwargs["aws_session_token"] = aws_session_token

        session = boto3.session.Session(**session_kwargs)

        self.client = session.client(
            "s3",
            endpoint_url=endpoint_url,
        )

    async def upload_bytes(self, key: str, content: bytes, content_type: str) -> str:
        try:
            await asyncio.to_thread(
                self.client.put_object,
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
            return f"s3://{self.bucket_name}/{key}"
        except Exception as exc:
            raise S3StorageError(f"Failed to upload object to S3: {key}") from exc

    async def download_bytes(self, key: str) -> bytes:
        try:
            response = await asyncio.to_thread(
                self.client.get_object,
                Bucket=self.bucket_name,
                Key=key,
            )
            body = response["Body"].read()
            return body
        except Exception as exc:
            raise S3StorageError(f"Failed to download object from S3: {key}") from exc