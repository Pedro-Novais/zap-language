from datetime import datetime, timezone
from loguru import logger

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import PasswordHasherService
from core.shared.errors import (
    NoVerificationCodeWasGeneratedError,
    CodeExpiredError,
    InvalidVerificationCodeError,
    UserNotFoundError,
)
from core.model.enum.verification_code_type import VerificationCodeType


class ResetPasswordInteractor:

    def __init__(
        self,
        user_repository: UserRepository,
        phone_verification_repository: PhoneVerificationRepository,
        password_hasher_service: PasswordHasherService,
    ) -> None:

        self.user_repository = user_repository
        self.phone_verification_repository = phone_verification_repository
        self.password_hasher_service = password_hasher_service

    def execute(self, token: str, new_password: str) -> None:
        logger.info("Processing password reset using token")

        verification = self.phone_verification_repository.get_verification_by_code(
            code=token,
            code_type=VerificationCodeType.EMAIL,
        )

        if verification is None:
            logger.error("No verification found for given token")
            raise InvalidVerificationCodeError()

        if datetime.now(timezone.utc) > verification.expires_at:
            logger.error("Verification token expired")
            raise CodeExpiredError()

        email = verification.value
        if not email:
            logger.error("Verification does not contain an email in value")
            raise NoVerificationCodeWasGeneratedError()

        user = self.user_repository.get_user_by_email(email=email)
        if user is None:
            logger.error(f"No user found for email {email}")
            raise UserNotFoundError()

        new_password_hash = self.password_hasher_service.hash(new_password)

        self.user_repository.update_password(
            user_id=str(user.id),
            new_password_hash=new_password_hash,
        )

        # remove any existing codes for this user
        self.phone_verification_repository.delete_old_verification_code(user_id=str(user.id))

        logger.info(f"Password reset successful for user {email}")
