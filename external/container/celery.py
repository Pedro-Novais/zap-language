from celery import Celery
from external.container.redis import redis_url


app_celery = Celery("zap_language_worker", broker=redis_url)
