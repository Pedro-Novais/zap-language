from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.shared.errors import EmailAlreadyExistsError


class CreateUserInteractor:
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
    ) -> None:
        
        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service

    def execute(
        self,
        name: str,
        email: str,
        password: str,
    ) -> None:
        
        logger.info(f"Creating user with email: {email}")
        
        if self.user_repository.get_user_by_email(email):
            logger.error(f"Email '{email}' already exists")
            raise EmailAlreadyExistsError(email=email)
        
        password_hash = self.password_hasher_service.hash(password=password)
        self.user_repository.create(
            name=name,
            email=email,
            password_hash=password_hash,
        )
        return