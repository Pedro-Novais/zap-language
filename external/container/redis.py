import os
from dotenv import load_dotenv

import redis


load_dotenv()

redis_url = os.getenv('REDIS_URL')
redis_client = redis.from_url(url=redis_url, decode_responses=True)
