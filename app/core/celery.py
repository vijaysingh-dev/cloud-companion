from celery import Celery
from app.core.config import settings


celery = Celery(
    "cloud_companion",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # reliability
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # retries
    task_default_retry_delay=5,
    task_max_retries=3,
)

celery.autodiscover_tasks(["app.tasks"])
