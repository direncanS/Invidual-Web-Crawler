from celery import Celery
from app.core.config import settings

celery = Celery(
    "worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.task_serializer = "json"
celery.conf.result_serializer = "json"
celery.conf.accept_content = ["json"]

celery.conf.include = [
    "app.tasks.crawl_tasks",
    "app.tasks.pdf_tasks",
    "app.tasks.wordcloud_tasks",
]