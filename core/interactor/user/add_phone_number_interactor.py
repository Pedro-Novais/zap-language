import secrets
from datetime import datetime, timezone

from loguru import logger

from core.interface.repository import (
    UserRepository,
    PhoneVerificationRepository,
)
from core.interface.service import WhatsappService
from core.shared.errors import (
    InvalidPhoneNumberError,
    InvalidVerificationCodeError,
    UserAlreadyHasPhoneNumberError,
    NoVerificationCodeWasGeneratedError,
    MaxAttemptsReachedError,
    CodeExpiredError,
)
from core.model import PhoneVerificationModel


class AddPhoneNumberInteractor:
    
    MESSAGE_TEMPLATE = "Seu código de verificação é: {code}"
    MAX_ATTEMPTS = 5
    
    def __init__(
        self,
        whatsapp_service: WhatsappService,
        user_repository: UserRepository,
        phone_verification_repository: PhoneVerificationRepository,
    ) -> None:
        
        self.whatsapp_service = whatsapp_service
        self.user_repository = user_repository
        self.phone_verification_repository = phone_verification_repository

    def add_phone_number(
        self,
        user_id: str,
        phone_number: str,
    ) -> None:
        
        logger.info(f"Adding phone number {phone_number} to user {user_id}")
        
        self._validate_format_of_phone_number(phone_number=phone_number)
        self._check_if_user_has_phone_number(user_id=user_id)
        
        self.phone_verification_repository.delete_old_verification_code(user_id=user_id)
        
        verification_code = self._generate_verification_code()
        self.phone_verification_repository.create_verification_code(
            user_id=user_id,
            phone_number=phone_number,
            code=verification_code,
        )
        
        logger.info(f"Sending verification code to {phone_number}")
        self.whatsapp_service.send_text(
            phone=phone_number,
            message=self.MESSAGE_TEMPLATE.format(code=verification_code)
        )
        
        return
    
    def verify_phone_number_code(
        self,
        user_id: str,
        phone_number: str,
        code: str,
    ) -> None:
        
        logger.info(f"Verifying code for phone number {phone_number}, code provided: {code}")
        
        self._validate_format_of_phone_number(phone_number=phone_number)
        self._check_if_user_has_phone_number(user_id=user_id)
        
        saved_code_info = self.phone_verification_repository.get_verification_code_information(
            user_id=user_id,
            phone_number=phone_number,
        )
        if saved_code_info is None:
            logger.error("No verification code found for the provided phone number")
            raise NoVerificationCodeWasGeneratedError()
        
        self._check_if_verification_code_is_valid(saved_code_info=saved_code_info)
        if saved_code_info.code != code:
            logger.error("Invalid verification code provided")
            self.phone_verification_repository.set_attempts_in_verification_code(
                code_id=saved_code_info.id,
                attempts=saved_code_info.attempts + 1,
            )
            raise InvalidVerificationCodeError()
        
        logger.info(f"Phone number {phone_number} verified successfully for user {user_id}")
        self.phone_verification_repository.delete_old_verification_code(user_id=user_id)
        self.user_repository.insert_phone_number_by_user_id(
            user_id=user_id,
            phone_number=phone_number,
        )
        return
    
    def _check_if_user_has_phone_number(
        self,
        user_id: str,
    ) -> None:
        
        phone_number = self.user_repository.get_phone_number_by_user_id(user_id=user_id)
        if phone_number is not None:
            logger.error(f"User already has a phone number: {phone_number}")
            raise UserAlreadyHasPhoneNumberError()
    
    def _check_if_verification_code_is_valid(
        self,
        saved_code_info: PhoneVerificationModel,
    ) -> None:
        
        logger.info("Checking if verification code is still valid")
        
        if datetime.now(timezone.utc) > saved_code_info.expires_at:
            logger.error("Verification code has expired")
            raise CodeExpiredError()
        
        if saved_code_info.attempts >= self.MAX_ATTEMPTS:
            logger.error("Maximum verification attempts exceeded")
            raise MaxAttemptsReachedError()
        
        logger.info("Verification code is valid")
    
    @staticmethod
    def _validate_format_of_phone_number(
        phone_number: str,
    ) -> None:
        
        if not phone_number.startswith("55") or len(phone_number) < 13:
            logger.error(f"Invalid phone number format: {phone_number}")
            raise InvalidPhoneNumberError()
        
    @staticmethod
    def _generate_verification_code() -> str:
        return str(secrets.randbelow(900000) + 100000)
    