from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.shared.errors import (
    UserNotFoundError,
    IncorrectPasswordProvidedError,
)


class ChangePasswordInteractor:
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
    ) -> None:
        
        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service

    def execute(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
    ) -> None:
        
        logger.info(f"Changing password for user_id: {user_id}")
        
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            logger.error(f"User with id '{user_id}' not found")
            raise UserNotFoundError()
        
        # Verify if old password is correct
        password_is_correct = self.password_hasher_service.verify(
            password_sended=old_password,
            password_saved=user.password,
        )
        if not password_is_correct:
            logger.error("Incorrect old password provided")
            raise IncorrectPasswordProvidedError()
        
        # Hash new password
        new_password_hash = self.password_hasher_service.hash(new_password)
        
        # Update password in database
        self.user_repository.update_password(
            user_id=user_id,
            new_password_hash=new_password_hash,
        )
        
        logger.info(f"Password changed successfully for user_id: {user_id}")
