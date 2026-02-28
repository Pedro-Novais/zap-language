from typing import Optional

import redis

from core.interface.service import RedisService
from core.manager.key import RedisKeyManager


class RedisServiceImpl(RedisService):

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
    
    def has_lock_global_ia(
        self,
    ) -> bool:
        
        return self.redis_client.get(RedisKeyManager.global_ia_lock()) is not None
    
    def set_lock_global_ia(
        self,
        timeout,
    ) -> None:
        
        self.redis_client.set(
            name=RedisKeyManager.global_ia_lock(),
            value="0",
            ex=timeout,
        )
        
    def get_api_user_cached(
        self,
        user_id: str,
    ) -> Optional[str]:
        
        return self.redis_client.get(RedisKeyManager.api_user_cached(user_id=user_id))
    
    def set_api_user_cached(
        self,
        user_id: str,
    ) -> None:
        
        self.redis_client.setex(RedisKeyManager.api_user_cached(user_id=user_id), 300, "1")
    