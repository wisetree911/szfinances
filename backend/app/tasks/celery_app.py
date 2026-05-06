from app.core.config import settings
from celery import Celery

celery_app = Celery(
    'sz_finances',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.tbank'],
)

celery_app.conf.update(
    accept_content=['json'],
    enable_utc=True,
    result_expires=3600,
    result_serializer='json',
    task_serializer='json',
    task_track_started=True,
    timezone='UTC',
)
