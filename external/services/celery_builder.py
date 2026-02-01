import os
from celery import Celery
import redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)

def make_celery():
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    celery_app = Celery(
        "zap_language_worker",
        broker=redis_url,
        backend=redis_url
    )
    
    celery_app.conf.update(
        broker_connection_retry_on_startup=True,
        task_always_eager=True ,
    )
    
    return celery_app

celery = make_celery()