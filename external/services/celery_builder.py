import os
import redis
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL')
env_production = os.getenv("ENV") == "production"
redis_client = redis.from_url(redis_url, decode_responses=True)
