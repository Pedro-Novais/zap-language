import os
from dotenv import load_dotenv

load_dotenv()
import redis

redis_url = os.getenv('REDIS_URL')
redis_client = redis.from_url(redis_url, decode_responses=True)
