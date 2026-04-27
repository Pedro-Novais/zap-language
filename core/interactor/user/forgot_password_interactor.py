from loguru import logger

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import SendEmailService
from core.shared.errors import UserNotFoundError
from secrets import token_urlsafe
from core.model.enum.verification_code_type import VerificationCodeType


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
            return

        reset_token = token_urlsafe(48)
        self.phone_verification_repository.create_verification_code(
            user_id=user.id,
            value=email,
            code=reset_token,
            code_type=VerificationCodeType.EMAIL,
        )
            # Remove apenas códigos antigos de reset de senha do tipo EMAIL para este usuário
        self.phone_verification_repository.delete_old_verification_code(
            user_id=user.id,
            code_type=VerificationCodeType.EMAIL,
        )
        reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
        # TODO - Remove comment after create email template and configure email service
        # self.send_email_service.send_email(
        #     to=email,
        #     subject="Reset Your Password",
        #     body=f"Click here to reset your password: {reset_link}",
        # )

        logger.info(f"Password reset email sent to {email}")