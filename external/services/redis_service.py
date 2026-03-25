from typing import Optional
from loguru import logger

import redis

from core.shared.model import RedisConfig
from core.interface.service import RedisService
from core.manager.key import RedisKeyManager


class RedisServiceImpl(RedisService):

    def __init__(
        self,
        config: RedisConfig,
        redis_client: redis.Redis,
    ) -> None:
        
        self.config = config
        
        self.redis_client = redis_client
    
    def notify_settings_changed(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.setex(
            name=RedisKeyManager.update_user_profile(phone=phone), 
            value="1", 
            time=self.config.timeout_to_notify_user_changes,
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
        
        logger.info(f"[RedisService] Deleting update to user profile for {phone}")
        self.redis_client.delete(RedisKeyManager.update_user_profile(phone=phone))
    
    def has_lock_global_ia( 
        self,
    ) -> bool:
        
        return self.redis_client.get(RedisKeyManager.global_ia_lock()) is not None
    
    def set_lock_global_ia(
        self,
        timeout: Optional[int] = None,
    ) -> None:
        
        expiration = timeout or self.config.time_to_increment_in_ai_lock
        self.redis_client.set(
            name=RedisKeyManager.global_ia_lock(),
            value="0",
            ex=expiration,
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
        
        self.redis_client.set(
            name=RedisKeyManager.api_user_cached(user_id=user_id),
            ex=self.config.timeout_user_cached_to_api,
            value="1",
            )
        
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
                ex=self.config.timeout_to_processing_phone,
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
        
        logger.info(f"[RedisService] Deleting processing phone for {phone}")
        self.redis_client.delete(RedisKeyManager.processing_phone(phone=phone))
        
    def ban_phone(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.set(
            name=RedisKeyManager.black_list_phone(phone=phone),
            ex=self.config.timeout_to_ban_phone,
            value="1",
        )
        
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
        
        self.redis_client.set(
            name=RedisKeyManager.user_profile(phone=phone), 
            ex=self.config.timeout_to_user_profile, 
            value=user_profile,
        )
        
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
            end=self.config.limit_message_history,
        )
        return messages_history
    
    def set_message_history(
        self,
        phone: str,
        message: str,
    ) -> None:
        
        key = RedisKeyManager.user_message_history(phone=phone)
        self.redis_client.lpush(key, message)
        self.redis_client.ltrim(key, 0, self.config.limit_message_history)
        self.redis_client.expire(key, self.config.timeout_to_message_history)
        
    def delete_message_history(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.user_message_history(phone=phone))
        
    def api_user_cached(
        self,
        user_id: str,
    ) -> str:
        
        return self.redis_client.get(RedisKeyManager.api_user_cached(user_id=user_id))
    
    def set_conversation_session(
        self,
        phone: str,
        session: str,
    ) -> None:
        
        # TODO - Create a timeout config
        self.redis_client.set(
            name=RedisKeyManager.conversation_session(phone=phone), 
            ex=120, 
            value=session,
        )
    
    def get_conversation_session(
        self,
        phone: str,
    ) -> None:
        
        return self.redis_client.get(RedisKeyManager.conversation_session(phone=phone))
    
    def delete_conversation_session(
        self,
        phone: str,
    ) -> None:
        
        self.redis_client.delete(RedisKeyManager.conversation_session(phone=phone))
    