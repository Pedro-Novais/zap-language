from datetime import datetime

import pytest
from faker import Faker

from core.interactor.user.user_interactor import UserInteractor
from core.interface.repository import UserRepository
from core.model import UserModel
from core.shared.errors import UserNotFoundError

fake = Faker()


class TestUserInteractor:

    @pytest.fixture
    def interactor(self, user_repository_mock: UserRepository):
        return UserInteractor(user_repository=user_repository_mock)

    def test_get_user_info_success(
        self, 
        interactor: UserInteractor, 
        user_repository_mock: UserRepository,
    ) -> None:
        
        user_id = fake.uuid4()
        expected_user = UserModel(
            id=user_id,
            email="test@example.com",
            name="Test User",
            phone="5511999999999",
            whatsapp_enabled=True,
            created_at=datetime.now(),
            study_settings=None,
            password="hashed_password",
            current_topic=None,
        )

        user_repository_mock.get_user_by_id.return_value = expected_user

        user = interactor.get_user_info(user_id=user_id)

        user_repository_mock.get_user_by_id.assert_called_once_with(user_id=user_id)
        assert user == expected_user

    def test_get_user_info_not_found(
        self, 
        interactor: UserInteractor, 
        user_repository_mock: UserRepository,
    ) -> None:
        
        user_id = fake.uuid4()
        user_repository_mock.get_user_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            interactor.get_user_info(user_id=user_id)
