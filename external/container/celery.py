import os

from celery import Celery
from external.container.redis import redis_url


app_celery = Celery(
    "zap_language_worker", 
    broker=redis_url,
    include=[
        "worker.worker",
    ],
)

is_production = os.getenv("ENV") == "production"
app_celery.conf.task_always_eager = not is_production
