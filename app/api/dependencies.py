from app.infrastructure.queue.sqs_queue_adapter import SqsQueueAdapter
from app.infrastructure.storage.s3_storage_adapter import S3StorageAdapter
from app.db.unit_of_work.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infrastructure.config.settings import settings
from app.application.use_cases.ingest_document import IngestDocumentUseCase
from app.infrastructure.ids.uuid_generator import UuidGenerator
from app.infrastructure.time.system_clock import SystemClock

def get_uow_factory():
    return SqlAlchemyUnitOfWork


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
        endpoint_url=settings.SQS_ENDPOINT_URL,
    )
    
def get_id_generator():
    return UuidGenerator()


def get_clock():
    return SystemClock()

def get_ingest_document_use_case():
    return IngestDocumentUseCase(
        uow_factory=get_uow_factory(),
        storage=get_object_storage(),
        queue=get_queue(),
        id_generator=get_id_generator(),
        clock=get_clock(),
    )
