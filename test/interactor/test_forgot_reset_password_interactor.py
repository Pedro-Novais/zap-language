import pytest
from unittest.mock import ANY, create_autospec
from datetime import datetime, timedelta, timezone
from faker import Faker

from core.interactor.user.forgot_password_interactor import ForgotPasswordInteractor
from core.interactor.user.reset_password_interactor import ResetPasswordInteractor
from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import SendEmailService, PasswordHasherService
from core.model import UserModel, PhoneVerificationModel
from core.model.enum.verification_code_type import VerificationCodeType
from core.shared.errors import (
    UserNotFoundError,
    InvalidVerificationCodeError,
    CodeExpiredError,
    NoVerificationCodeWasGeneratedError,
    UserNotFoundError as UserNotFoundError2,
)

fake = Faker()


class TestForgotPasswordInteractor:

    @pytest.fixture
    def interactor(self, user_repository_mock: UserRepository, phone_verification_repository_mock: PhoneVerificationRepository):
        send_email_service_mock = create_autospec(spec=SendEmailService, instance=True)
        return ForgotPasswordInteractor(
            user_repository=user_repository_mock,
            send_email_service=send_email_service_mock,
            phone_verification_repository=phone_verification_repository_mock,
        )

    def test_should_generate_token_and_send_email(self, interactor: ForgotPasswordInteractor, user_repository_mock: UserRepository, phone_verification_repository_mock: PhoneVerificationRepository):
        user_id = fake.uuid4()
        email = "user@example.com"
        user_repository_mock.get_user_by_email.return_value = UserModel(
            id=user_id,
            email=email,
            name="Test",
            phone=None,
            whatsapp_enabled=False,
            created_at=datetime.now(timezone.utc),
            study_settings=None,
            password="hash",
            current_topic=None,
        )

        interactor.execute(email=email)

        user_repository_mock.get_user_by_email.assert_called_once_with(email=email)
        phone_verification_repository_mock.create_verification_code.assert_called_once()
        called_kwargs = phone_verification_repository_mock.create_verification_code.call_args.kwargs
        assert called_kwargs["user_id"] == user_id
        assert called_kwargs["value"] == email
        assert called_kwargs["code"] is not None
        assert called_kwargs["code_type"] == VerificationCodeType.EMAIL

    def test_should_raise_when_user_not_found(self, interactor: ForgotPasswordInteractor, user_repository_mock: UserRepository):
        user_repository_mock.get_user_by_email.return_value = None
        with pytest.raises(UserNotFoundError):
            interactor.execute(email="missing@example.com")


class TestResetPasswordInteractor:

    @pytest.fixture
    def interactor(self, user_repository_mock: UserRepository, phone_verification_repository_mock: PhoneVerificationRepository, password_hasher_service_mock: PasswordHasherService):
        return ResetPasswordInteractor(
            user_repository=user_repository_mock,
            phone_verification_repository=phone_verification_repository_mock,
            password_hasher_service=password_hasher_service_mock,
        )

    def _make_verification(self, token: str, email: str | None, expires_delta_seconds: int = 300):
        now = datetime.now(timezone.utc)
        return PhoneVerificationModel(
            id=fake.uuid4(),
            user_id=fake.uuid4(),
            value=email,
            code=token,
            attempts=0,
            expires_at=now + timedelta(seconds=expires_delta_seconds),
            created_at=now,
            code_type=VerificationCodeType.EMAIL,
        )

    def test_should_reset_password_successfully(self, interactor: ResetPasswordInteractor, user_repository_mock: UserRepository, phone_verification_repository_mock: PhoneVerificationRepository, password_hasher_service_mock: PasswordHasherService):
        token = "resettoken"
        email = "user2@example.com"
        verification = self._make_verification(token=token, email=email)
        phone_verification_repository_mock.get_verification_by_code.return_value = verification

        user_id = fake.uuid4()
        user_repository_mock.get_user_by_email.return_value = UserModel(
            id=user_id,
            email=email,
            name="Test",
            phone=None,
            whatsapp_enabled=False,
            created_at=datetime.now(timezone.utc),
            study_settings=None,
            password="old_hash",
            current_topic=None,
        )

        password_hasher_service_mock.hash.return_value = "new_hash"

        interactor.execute(token=token, new_password="new_password")

        password_hasher_service_mock.hash.assert_called_once_with("new_password")
        user_repository_mock.update_password.assert_called_once_with(
            user_id=str(user_id),
            new_password_hash="new_hash",
        )
        phone_verification_repository_mock.delete_old_verification_code.assert_called_once_with(user_id=str(user_id))

    def test_should_raise_when_token_invalid(self, interactor: ResetPasswordInteractor, phone_verification_repository_mock: PhoneVerificationRepository):
        phone_verification_repository_mock.get_verification_by_code.return_value = None
        with pytest.raises(InvalidVerificationCodeError):
            interactor.execute(token="badtoken", new_password="x")

    def test_should_raise_when_token_expired(self, interactor: ResetPasswordInteractor, phone_verification_repository_mock: PhoneVerificationRepository):
        token = "expiredtoken"
        verification = self._make_verification(token=token, email="e@example.com", expires_delta_seconds=-10)
        phone_verification_repository_mock.get_verification_by_code.return_value = verification
        with pytest.raises(CodeExpiredError):
            interactor.execute(token=token, new_password="x")

    def test_should_raise_when_no_email_in_verification(self, interactor: ResetPasswordInteractor, phone_verification_repository_mock: PhoneVerificationRepository):
        token = "notoken"
        verification = self._make_verification(token=token, email=None)
        phone_verification_repository_mock.get_verification_by_code.return_value = verification
        with pytest.raises(NoVerificationCodeWasGeneratedError):
            interactor.execute(token=token, new_password="x")

    def test_should_raise_when_user_not_found(self, interactor: ResetPasswordInteractor, phone_verification_repository_mock: PhoneVerificationRepository, user_repository_mock: UserRepository):
        token = "t"
        email = "notfound@example.com"
        verification = self._make_verification(token=token, email=email)
        phone_verification_repository_mock.get_verification_by_code.return_value = verification
        user_repository_mock.get_user_by_email.return_value = None
        with pytest.raises(UserNotFoundError2):
            interactor.execute(token=token, new_password="x")
