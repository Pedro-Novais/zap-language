import json
import redis
from typing import Optional

from loguru import logger

from core.interface.repository import UserRepository
from core.model import UserModel


class UserManager:
    
    KEY_USER_PROFILE = "user:profile:{phone}"
    
    def __init__(
        self, 
        redis_client: redis.Redis, 
        user_repository: UserRepository, 
        ttl: int = 3600,
    ) -> None:
        
        self.redis = redis_client
        self.user_repository = user_repository
        self.TTL = ttl

    def get_study_settings_by_phone(
        self, 
        phone: str,
    ) -> Optional[UserModel]:
        
        key = self._get_key_user_profile(phone=phone)
        logger.info(f"👤 Buscando perfil de {phone}")
        
        cached_user = self.redis.get(key)
        if cached_user:
            logger.info(f"👤 Cache Hit para perfil de {phone}")
            return UserModel.model_validate_json(cached_user)

        logger.info(f"👤 Cache Miss para perfil de {phone}. Buscando no banco...")
        user_data = self.user_repository.get_user_by_phone_number(phone=phone)
        
        if not user_data:
            logger.info(f"👤 Usuário não encontrado para {phone}")
            return None

        self.redis.setex(key, self.TTL, user_data.model_dump_json())
        return user_data

    def invalidate_cache(
        self, 
        phone: str,
    ) -> None:
        
        self.redis.delete(f"user:profile:{phone}")
        
    def _get_key_user_profile(
        self, 
        phone: str,
    ) -> str:
        
        return self.KEY_USER_PROFILE.format(phone=phone)