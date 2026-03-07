from typing import Optional

from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import RedisService
from core.model import UserModel


class UserService:
    
    def __init__(
        self, 
        redis_service: RedisService,
        user_repository: UserRepository, 
    ) -> None:
        
        self.user_repository = user_repository
        
        self.redis_service = redis_service

    def get_user_profile(
        self, 
        phone: str,
    ) -> Optional[UserModel]:
        
        logger.info(f"Getting user profile for {phone}")
        
        user_profile_cached = self.redis_service.get_user_profile(phone=phone)
        if user_profile_cached:
            logger.info(f"Cache hit to phone: {phone}")
            return UserModel.model_validate_json(user_profile_cached)

        logger.info(f"Cache miss to phone: {phone}. Getting from database")
        user_profile = self.user_repository.get_user_by_phone_number(phone=phone)
        if not user_profile:
            logger.error(f"User not found for phone: {phone}")
            return None

        self.redis_service.set_user_profile(
            phone=phone,
            user_profile=user_profile.model_dump_json(),
        )
        return user_profile

    def invalidate_user_cache(
        self, 
        phone: str,
    ) -> None:
        
        logger.info(f"Invalidating user cache for {phone}")
        
        self.redis_service.delete_user_profile(phone=phone)
    