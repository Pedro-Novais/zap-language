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
        self.timeout = 30
        self.limit = 10
    
    def notify_settings_changed(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.setex(
            name=RedisKeyManager.update_user_profile(phone=phone), 
            value="1", 
            time=self.timeout,
        )
        
    def has_update_to_user_profile(
        self,
        phone: str,
    ) -> bool:
        
        return bool(self.redis_client.exists(RedisKeyManager.update_user_profile(phone=phone)))
    
    def delete_update_user_profile(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.update_user_profile(phone=phone))
    
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
        
    def user_is_banned(
        self,
        phone: str,
    ) -> bool:
        
        return bool(self.redis_client.exists(RedisKeyManager.black_list_phone(phone=phone)))
    
    def set_current_processing_phone(
        self,
        phone: str,
    ) -> None:
        
        return bool(
            self.redis_client.set(
                name=RedisKeyManager.processing_phone(phone=phone),
                value="locked",
                ex=self.timeout,
                nx=True,
            )
        )
        
    def user_beeing_processed(
        self,
        phone: str,
    ) -> bool:
        
        return bool(self.redis_client.exists(RedisKeyManager.processing_phone(phone=phone)))
    
    def delete_processing_phone(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.processing_phone(phone=phone))
        
    def ban_phone(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.setex(RedisKeyManager.black_list_phone(phone=phone), self.timeout, "1")
        
    def get_user_profile(
        self,
        phone: str,
    ) -> Optional[str]:
        
        return self.redis_client.get(RedisKeyManager.user_profile(phone=phone))
    
    def set_user_profile(
        self,
        phone: str,
        user_profile: str,
    ) -> None:
        
        self.redis_client.setex(RedisKeyManager.user_profile(phone=phone), self.timeout, user_profile)
        
    def delete_user_profile(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.user_profile(phone=phone))
        
    def get_message_history(
        self,
        phone: str,
    ) -> Optional[str]:
        
        messages_history = self.redis_client.lrange(
            name=RedisKeyManager.user_message_history(phone=phone), 
            start=0, 
            end=self.timeout-1,
        )
        return messages_history
    
    def set_message_history(
        self,
        phone: str,
        message: str,
    ) -> None:
        
        key = RedisKeyManager.user_message_history(phone=phone)
        self.redis_client.lpush(key, message)
        self.redis_client.ltrim(key, 0, self.limit - 1)
        self.redis_client.expire(key, self.timeout)
        
    def delete_message_history(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.user_message_history(phone=phone))
    