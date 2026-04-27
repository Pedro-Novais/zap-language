import secrets
from loguru import logger

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import SendEmailService
from core.model.enum.verification_code_type import VerificationCodeType
from core.shared.errors import UserNotFoundError


class RequestEmailVerificationInteractor:
    def __init__(
        self,
        user_repository: UserRepository,
        phone_verification_repository: PhoneVerificationRepository,
        send_email_service: SendEmailService,
    ) -> None:
        
        self.user_repository = user_repository
        self.phone_verification_repository = phone_verification_repository
        self.send_email_service = send_email_service

    def execute(
        self,
        user_id: str,
    ) -> None:
        
        logger.info(f"Requesting email verification for user_id: {user_id}")
        
        user = self.user_repository.get_user_by_id(user_id=user_id)
        
        if not user:
            logger.error(f"User with id '{user_id}' not found")
            raise UserNotFoundError()
        
        if user.is_valid:
            logger.warning(f"User '{user_id}' email is already validated")
            return
        
        self.phone_verification_repository.delete_old_verification_code(
            user_id=user_id,
            code_type=VerificationCodeType.EMAIL,
        )
        
        verification_code = self._generate_verification_code()
        
        self.phone_verification_repository.create_verification_code(
            user_id=user_id,
            value=user.email,
            code=verification_code,
            code_type=VerificationCodeType.EMAIL,
        )
        
        self.send_email_service.send_email(
            to=user.email,
            subject="Zap Language - Confirme seu e-mail",
            body=f"<p>Seu código de validação é: <strong>{verification_code}</strong>. Este código expira em 10 minutos.</p>",
        )
        
        return
        
    @staticmethod
    def _generate_verification_code() -> str:
        return str(secrets.randbelow(900000) + 100000)
