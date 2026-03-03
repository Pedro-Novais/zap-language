import pytest
from unittest.mock import ANY
from faker import Faker

from core.interactor.user.add_phone_number_interactor import AddPhoneNumberInteractor
from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import WhatsappService
from core.shared.errors import (
    InvalidPhoneNumberError,
    UserAlreadyHasPhoneNumberError,
)

fake = Faker()


class TestAddPhoneNumberInteractor:

    @pytest.fixture
    def interactor(
        self, 
        whatsapp_service_mock: WhatsappService, 
        user_repository_mock: UserRepository, 
        phone_verification_repository_mock: PhoneVerificationRepository,
    ):
        return AddPhoneNumberInteractor(
            whatsapp_service=whatsapp_service_mock,
            user_repository=user_repository_mock,
            phone_verification_repository=phone_verification_repository_mock,
        )


    def test_should_add_phone_number_successfully(
        self, 
        interactor: AddPhoneNumberInteractor, 
        user_repository_mock: UserRepository, 
        phone_verification_repository_mock: PhoneVerificationRepository, 
        whatsapp_service_mock: WhatsappService
    ) -> None:

        user_id = fake.uuid4()
        phone_number = "5511999999999"
        
        user_repository_mock.get_phone_number_by_user_id.return_value = None
        
        interactor.add_phone_number(user_id=user_id, phone_number=phone_number)
        
        user_repository_mock.get_phone_number_by_user_id.assert_called_once_with(user_id=user_id)
        phone_verification_repository_mock.delete_old_verification_code.assert_called_once_with(user_id=user_id)
        
        phone_verification_repository_mock.create_verification_code.assert_called_once_with(
            user_id=user_id,
            phone_number=phone_number,
            code=ANY,
        )
        
        whatsapp_service_mock.send_text.assert_called_once()


    def test_should_raise_error_when_phone_format_is_invalid(
        self, 
        interactor: AddPhoneNumberInteractor,
        ) -> None:

        with pytest.raises(InvalidPhoneNumberError):
            interactor.add_phone_number(user_id=fake.uuid4(), phone_number="11999999999")


    def test_should_raise_error_when_user_already_has_phone(
        self, 
        interactor: AddPhoneNumberInteractor, 
        user_repository_mock: UserRepository,
        ) -> None:

        user_repository_mock.get_phone_number_by_user_id.return_value = "5511888888888"
        
        with pytest.raises(UserAlreadyHasPhoneNumberError):
            interactor.add_phone_number(user_id=fake.uuid4(), phone_number="5511999999999")
            