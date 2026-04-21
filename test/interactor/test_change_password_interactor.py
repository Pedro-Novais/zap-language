from datetime import datetime

import pytest
from faker import Faker

from core.interactor.user.change_password_interactor import ChangePasswordInteractor
from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.model import UserModel
from core.shared.errors import (
    IncorrectPasswordProvidedError,
    UserNotFoundError,
)

fake = Faker()


class TestChangePasswordInteractor:

    @pytest.fixture
    def interactor(
        self,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
    ):
        return ChangePasswordInteractor(
            user_repository=user_repository_mock,
            password_hasher_service=password_hasher_service_mock,
        )

    def test_should_change_password_successfully(
        self,
        interactor: ChangePasswordInteractor,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
    ) -> None:

        user_id = fake.uuid4()
        old_password = "old_password"
        new_password = "new_password"
        new_password_hash = "hashed_new_password"

        user_repository_mock.get_user_by_id.return_value = UserModel(
            id=user_id,
            email="test@example.com",
            name="Test User",
            phone="5511999999999",
            whatsapp_enabled=True,
            created_at=datetime.now(),
            study_settings=None,
            password="saved_hashed_password",
            current_topic=None,
        )
        password_hasher_service_mock.verify.return_value = True
        password_hasher_service_mock.hash.return_value = new_password_hash

        interactor.execute(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
        )

        user_repository_mock.get_user_by_id.assert_called_once_with(user_id=user_id)
        password_hasher_service_mock.verify.assert_called_once_with(
            password_sended=old_password,
            password_saved="saved_hashed_password",
        )
        password_hasher_service_mock.hash.assert_called_once_with(new_password)
        user_repository_mock.update_password.assert_called_once_with(
            user_id=user_id,
            new_password_hash=new_password_hash,
        )

    def test_should_raise_when_user_not_found(
        self,
        interactor: ChangePasswordInteractor,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
    ) -> None:

        user_repository_mock.get_user_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            interactor.execute(
                user_id=fake.uuid4(),
                old_password="old_password",
                new_password="new_password",
            )

        password_hasher_service_mock.verify.assert_not_called()
        password_hasher_service_mock.hash.assert_not_called()
        user_repository_mock.update_password.assert_not_called()

    def test_should_raise_when_old_password_is_incorrect(
        self,
        interactor: ChangePasswordInteractor,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
    ) -> None:

        user_id = fake.uuid4()
        user_repository_mock.get_user_by_id.return_value = UserModel(
            id=user_id,
            email="test@example.com",
            name="Test User",
            phone="5511999999999",
            whatsapp_enabled=True,
            created_at=datetime.now(),
            study_settings=None,
            password="saved_hashed_password",
            current_topic=None,
        )
        password_hasher_service_mock.verify.return_value = False

        with pytest.raises(IncorrectPasswordProvidedError):
            interactor.execute(
                user_id=user_id,
                old_password="wrong_password",
                new_password="new_password",
            )

        password_hasher_service_mock.hash.assert_not_called()
        user_repository_mock.update_password.assert_not_called()
