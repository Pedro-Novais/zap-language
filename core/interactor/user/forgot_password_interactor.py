from loguru import logger

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import SendEmailService
from core.shared.errors import UserNotFoundError
from secrets import token_urlsafe


class ForgotPasswordInteractor:

    def __init__(
        self,
        user_repository: UserRepository,
        send_email_service: SendEmailService,
        phone_verification_repository: PhoneVerificationRepository,
    ) -> None:

        self.user_repository = user_repository
        self.send_email_service = send_email_service
        self.phone_verification_repository = phone_verification_repository

    def execute(
        self,
        email: str,
    ) -> None:

        logger.info(f"Processing forgot password request for email: {email}")
        user = self.user_repository.get_user_by_email(email=email)
        if not user:
            logger.warning(f"User with email '{email}' not found")
            raise UserNotFoundError()
        reset_token = token_urlsafe(48)

        # save token in verification table as EMAIL type
        # phone_number left as None for email verifications
        self.phone_verification_repository.create_verification_code(
            user_id=str(user.id),
            phone_number=None,
            code=reset_token,
            code_type="EMAIL",
        )

        reset_link = f"https://yourapp.com/reset-password?token={reset_token}"

        self.send_email_service.send_email(
            to=email,
            subject="Reset Your Password",
            body=f"Click here to reset your password: {reset_link}",
        )

        logger.info(f"Password reset email sent to {email}")