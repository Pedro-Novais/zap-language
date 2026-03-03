from typing import  Any, Dict
from dataclasses import dataclass

from core.model.enum import SystemConfigKey 

    
@dataclass
class RedisConfig:
    timeout_lock_global_ia: int
    time_to_increment_in_ai_lock: int
    timeout_to_notify_user_changes: int
    timeout_to_notify_user_changes: int
    timeout_to_processing_phone: int
    timeout_to_ban_phone: int
    timeout_to_user_profile: int
    limit_message_history: int
    timeout_to_message_history: int
    timeout_user_cached_to_api: int

@dataclass
class ConversationManagerConfig:
    notify_user_when_banned: bool
    
@dataclass
class HistoryManagerConfig:
    limit_message_from_history: int
    
@dataclass
class CeleryConfig:
    max_retry: int
    retry_backoff: bool
    retry_backoff_max: int
    retry_jitter: bool
    timeout_to_message_lock_by_ai: int

@dataclass
class SystemConfig:
    celery: CeleryConfig
    redis: RedisConfig
    history: HistoryManagerConfig
    conversation: ConversationManagerConfig
    

class SystemConfigModel:
    def __init__(
        self, 
        configs: Dict[str, Any],
    ) -> None:

        self.celery = self._get_celery_config(configs=configs)
        self.redis = self._get_redis_config(configs=configs)
        self.history = self._get_history_manager_config(configs=configs)
        self.conversation = self._get_conversation_manager_config(configs=configs)
    
    def get_system_config(self) -> SystemConfig:
        
        return SystemConfig(
            celery=self.celery,
            redis=self.redis,
            history=self.history,
            conversation=self.conversation,
        )
    
    @staticmethod
    def _get_celery_config(configs: Dict[str, Any]) -> CeleryConfig:
        config = configs.get(SystemConfigKey.CELERY.value, {})
        return CeleryConfig(
            max_retry=config.get("max_retry", 3),
            retry_backoff=config.get("retry_backoff", True),
            retry_backoff_max=config.get("retry_backoff_max", 600),
            retry_jitter=config.get("retry_jitter", True),
            timeout_to_message_lock_by_ai=config.get("timeout_to_message_lock_by_ai", 15),
        )
        
    
    @staticmethod
    def _get_redis_config(configs: Dict[str, Any]) -> RedisConfig:
        config = configs.get(SystemConfigKey.REDIS.value, {})
        return RedisConfig(
            timeout_lock_global_ia=config.get("timeout_lock_global_ia", 15),
            time_to_increment_in_ai_lock=config.get("time_to_increment_in_ai_lock", 5),
            timeout_to_notify_user_changes=config.get("timeout_to_notify_user_changes", 300),
            timeout_to_processing_phone=config.get("timeout_to_processing_phone", 300),
            timeout_to_ban_phone=config.get("timeout_to_ban_phone", 1200),
            timeout_to_user_profile=config.get("timeout_to_user_profile", 300),
            limit_message_history=config.get("limit_message_history", 10),
            timeout_to_message_history=config.get("timeout_to_message_history", 300),
            timeout_user_cached_to_api=config.get("timeout_user_cached_to_api", 300),
        )
        
    @staticmethod
    def _get_conversation_manager_config(configs: Dict[str, Any]) -> ConversationManagerConfig:
        config = configs.get(SystemConfigKey.CONVERSATION_MANAGER.value, {})
        return ConversationManagerConfig(
            notify_user_when_banned=config.get("notify_user_when_banned", True),
        )
    
    @staticmethod
    def _get_history_manager_config(configs: Dict[str, Any]) -> HistoryManagerConfig:
        config = configs.get(SystemConfigKey.HISTORY_MANAGER.value, {})
        return HistoryManagerConfig(
            limit_message_from_history=config.get("limit_message_from_history", 10),
        )
    