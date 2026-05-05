from datetime import datetime

import jwt
import pytest
from faker import Faker

from core.interactor.user.google_login_interactor import GoogleLoginInteractor
from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.model import UserModel

fake = Faker()


class TestGoogleLoginInteractor:

    @pytest.fixture
    def interactor(
        self,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
    ):
        return GoogleLoginInteractor(
            user_repository=user_repository_mock,
            password_hasher_service=password_hasher_service_mock,
        )

    def test_should_create_user_when_email_does_not_exist(
        self,
        interactor: GoogleLoginInteractor,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
        monkeypatch,
    ) -> None:

        monkeypatch.setenv("SECRET_KEY", "test-secret")

        sub = "google-sub-123"
        email = "google-user@example.com"
        name = "Google User"
        expected_user = UserModel(
            id=fake.uuid4(),
            email=email,
            name=name,
            phone=None,
            whatsapp_enabled=False,
            created_at=datetime.now(),
            sub=sub,
            last_login=datetime.now(),
            study_settings=None,
            password="hashed-random-password",
            current_topic=None,
        )

        user_repository_mock.get_user_by_sub.return_value = None
        password_hasher_service_mock.hash.return_value = "hashed-random-password"
        user_repository_mock.create_google_user.return_value = expected_user

        token = interactor.execute(
            email=email,
            name=name,
            sub=sub,
        )

        user_repository_mock.get_user_by_sub.assert_called_once_with(sub=sub)
        password_hasher_service_mock.hash.assert_called_once()
        user_repository_mock.create_google_user.assert_called_once()
        decoded_token = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded_token["userId"] == str(expected_user.id)

    def test_should_update_last_login_when_user_already_exists(
        self,
        interactor: GoogleLoginInteractor,
        user_repository_mock: UserRepository,
        password_hasher_service_mock: PasswordHasherService,
        monkeypatch,
    ) -> None:

        monkeypatch.setenv("SECRET_KEY", "test-secret")

        existing_user = UserModel(
            id=fake.uuid4(),
            email="existing@example.com",
            name="Existing User",
            phone=None,
            whatsapp_enabled=False,
            created_at=datetime.now(),
            sub="old-sub",
            last_login=None,
            study_settings=None,
            password="hashed-password",
            current_topic=None,
        )
        updated_user = UserModel(
            id=existing_user.id,
            email=existing_user.email,
            name=existing_user.name,
            phone=existing_user.phone,
            whatsapp_enabled=existing_user.whatsapp_enabled,
            created_at=existing_user.created_at,
            sub="google-sub-456",
            last_login=datetime.now(),
            study_settings=None,
            password=existing_user.password,
            current_topic=None,
        )

        user_repository_mock.get_user_by_sub.return_value = existing_user
        user_repository_mock.update_google_login.return_value = updated_user

        token = interactor.execute(
            email=existing_user.email,
            name=existing_user.name,
            sub="google-sub-456",
        )

        user_repository_mock.get_user_by_sub.assert_called_once_with(sub="google-sub-456")
        password_hasher_service_mock.hash.assert_not_called()
        user_repository_mock.create_google_user.assert_not_called()
        user_repository_mock.update_google_login.assert_called_once()
        decoded_token = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded_token["userId"] == str(existing_user.id)