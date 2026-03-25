from app.infrastructure.queue.sqs_queue_adapter import SqsQueueAdapter
from app.infrastructure.config.settings import settings
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter


def get_object_storage():
    return S3StorageAdapter(
        bucket_name=settings.s3_bucket_name,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_session_token=settings.aws_session_token,
        endpoint_url=settings.s3_endpoint_url,
    )


def get_queue():
    return SqsQueueAdapter(
        queue_url=settings.sqs_queue_url,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_session_token=settings.aws_session_token,
        endpoint_url=settings.sqs_endpoint_url,
    )
