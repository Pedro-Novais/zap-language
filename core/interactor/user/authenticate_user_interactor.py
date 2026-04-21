from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.shared.auth import generate_auth_token
from core.shared.errors import (
    UserNotFoundError,
    IncorrectPasswordProvidedError,
)


class AuthenticateUserInteractor:
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
    ) -> None:
        
        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service

    def execute(
        self,
        email: str,
        password: str,
    ) -> str:
        
        logger.info(f"Authenticating user with email: {email}")
        
        user = self.user_repository.get_user_by_email(email)
        if not user:
            logger.error(f"Email '{email}' is not registered")
            raise UserNotFoundError(email=email)
        
        password_is_correct = self.password_hasher_service.verify(
            password_sended=password,
            password_saved=user.password,
        )
        if not password_is_correct:
            logger.error("Incorrect password provided")
            raise IncorrectPasswordProvidedError()
        
        logger.info(f"User authenticated with email: {email}")
        return generate_auth_token(user_id=str(user.id))