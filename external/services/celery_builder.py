import os
from celery import Celery
import redis
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL')
env_production = os.getenv("ENV") == "production"
redis_client = redis.from_url(redis_url, decode_responses=True)

def make_celery() -> Celery:
    
    celery_app = Celery(
        "zap_language_worker",
        broker=redis_url,
        backend=redis_url
    )
    celery_app.conf.update(
        broker_connection_retry_on_startup=True,
        task_always_eager=not env_production,
    )
    return celery_app


celery = make_celery()
