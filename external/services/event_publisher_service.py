import redis

from core.interface.service import EventPublisherService
from core.manager.key import RedisKeyManager


class EventPublisherServiceImpl(EventPublisherService):

    def __init__(
        self,
        redis_client: redis.Redis,
    ) -> None:
        
        self.redis_client = redis_client    
    
    def notify_settings_changed(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.setex(
            name=RedisKeyManager.update_user_profile(phone=phone), 
            value="1", 
            time=3600,
        )
    