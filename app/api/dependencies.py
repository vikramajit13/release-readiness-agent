from app.infrastructure.queue.sqs_queue_adapter import SqsQueueAdapter
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter
from app.db.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infrastructure.config.settings import settings

def get_uow_factory():
    return SqlAlchemyUnitOfWork()


def get_object_storage():
    return S3StorageAdapter(
        bucket_name=settings.BUCKET_NAME,
        region_name=settings.REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
        endpoint_url=settings.ENDPOINT_URL,
    )


def get_queue():
    return SqsQueueAdapter(
        queue_url=settings.SQS_QUEUE_URL,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
        endpoint_url=settings.sqs_endpoint_url,
    )
