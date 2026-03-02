import pytest
import uuid
from datetime import datetime

from core.manager.user_manager import UserManager
from core.interface.repository import UserRepository
from core.interface.service import RedisService
from core.model import UserModel


DEFAULT_PHONE = "5511999999999"


class TestUserManager:
    
    @pytest.fixture
    def manager(
        self, 
        redis_service_mock: RedisService, 
        user_repository_mock: UserRepository,
    ) -> UserManager:
        
        return UserManager(
            redis_service=redis_service_mock,
            user_repository=user_repository_mock,
        )

    def test_get_user_profile_cache_hit(
        self,
        manager: UserManager, 
        redis_service_mock: RedisService, 
        user_repository_mock: UserRepository,
    ) -> None:
        
        mock_user = get_user_model()
        redis_service_mock.get_user_profile.return_value = mock_user.model_dump_json()

        result = manager.get_user_profile(phone=DEFAULT_PHONE)

        assert result == mock_user
        redis_service_mock.get_user_profile.assert_called_once_with(phone=DEFAULT_PHONE)
        user_repository_mock.get_user_by_phone_number.assert_not_called()


    def test_get_user_profile_cache_miss_and_db_hit(
        self,
        manager: UserManager, 
        redis_service_mock: RedisService, 
        user_repository_mock: UserRepository,
    ) -> None:
        
        mock_user = get_user_model()
        
        redis_service_mock.get_user_profile.return_value = None
        user_repository_mock.get_user_by_phone_number.return_value = mock_user

        result = manager.get_user_profile(phone=DEFAULT_PHONE)

        assert result == mock_user
        redis_service_mock.set_user_profile.assert_called_once_with(
            phone=DEFAULT_PHONE,
            user_profile=mock_user.model_dump_json()
        )


    def test_get_user_profile_not_found(
        self,
        manager: UserManager, 
        redis_service_mock: RedisService, 
        user_repository_mock: UserRepository,
    ) -> None:

        phone = "000"
        redis_service_mock.get_user_profile.return_value = None
        user_repository_mock.get_user_by_phone_number.return_value = None

        result = manager.get_user_profile(phone)

        assert result is None
        redis_service_mock.set_user_profile.assert_not_called()


    def test_invalidate_user_cache(
        self,
        manager: UserManager, 
        redis_service_mock: RedisService, 
        ) -> None:

        phone = "5511777777777"

        manager.invalidate_user_cache(phone=phone)

        redis_service_mock.delete_user_profile.assert_called_once_with(phone=phone)
    

def get_user_model() -> UserModel:
    return UserModel(
        id=uuid.uuid4(), 
        phone=DEFAULT_PHONE, 
        name="Test User",
        whatsapp_enabled=True,
        created_at=datetime.now(),
        email="",
        password="",
        study_settings=None,
        current_topic=None,
    )
