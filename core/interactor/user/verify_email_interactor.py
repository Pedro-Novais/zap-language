from datetime import datetime, timezone
from loguru import logger

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.model.enum.verification_code_type import VerificationCodeType
from core.shared.errors import (
    UserNotFoundError,
    NoVerificationCodeWasGeneratedError,
    InvalidVerificationCodeError,
    CodeExpiredError,
    MaxAttemptsReachedError,
)
from core.model import PhoneVerificationModel


class VerifyEmailInteractor:
    MAX_ATTEMPTS = 5

    def __init__(
        self,
        user_repository: UserRepository,
        phone_verification_repository: PhoneVerificationRepository,
    ) -> None:
        
        self.user_repository = user_repository
        self.phone_verification_repository = phone_verification_repository

    def execute(
        self,
        user_id: str,
        code: str,
    ) -> None:
        
        logger.info(f"Verifying email code for user {user_id}")
        
        user = self.user_repository.get_user_by_id(user_id=user_id)
        
        if not user:
            logger.error(f"User with id '{user_id}' not found")
            raise UserNotFoundError()

        if user.is_valid:
            logger.warning(f"User '{user_id}' is already validated")
            return

        saved_code_info = self.phone_verification_repository.get_verification_code_information(
            user_id=user_id,
            value=user.email,
            code_type=VerificationCodeType.EMAIL,
        )
        
        if saved_code_info is None or saved_code_info.code_type != VerificationCodeType.EMAIL:
            logger.error("No email verification code found for user")
            raise NoVerificationCodeWasGeneratedError()
        
        self._check_if_verification_code_is_valid(
            saved_code_info=saved_code_info,
        )
        
        if saved_code_info.code != code:
            logger.error("Invalid email verification code provided")
            self.phone_verification_repository.set_attempts_in_verification_code(
                code_id=saved_code_info.id,
                attempts=saved_code_info.attempts + 1,
            )
            raise InvalidVerificationCodeError()
        
        self.user_repository.update_is_valid(
            user_id=user_id,
            is_valid=True,
        )
        
        self.phone_verification_repository.delete_old_verification_code(
            user_id=user_id,
            code_type=VerificationCodeType.EMAIL,
        )
        
        logger.info(f"Email verified successfully for user {user_id}")
        
        return

    def _check_if_verification_code_is_valid(
        self,
        saved_code_info: PhoneVerificationModel,
    ) -> None:
        
        if datetime.now(timezone.utc) > saved_code_info.expires_at:
            logger.error("Verification code has expired")
            raise CodeExpiredError()
        
        if saved_code_info.attempts >= self.MAX_ATTEMPTS:
            logger.error("Maximum verification attempts exceeded")
            raise MaxAttemptsReachedError()
            
        return
