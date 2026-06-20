from celery import Celery

from app.config import settings

celery = Celery(
    "skillbridge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    task_track_started=True,
    task_acks_late=True,  # retry if worker crashes mid-task
    worker_prefetch_multiplier=1,
)
