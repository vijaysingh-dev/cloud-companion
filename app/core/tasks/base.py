from app.core.celery import celery


class BaseTask(celery.Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_kwargs = {"max_retries": 3}
