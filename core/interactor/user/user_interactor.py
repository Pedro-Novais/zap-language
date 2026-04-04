from loguru import logger


from core.interface.repository import UserRepository
from core.model import UserModel
from core.shared.errors import UserNotFoundError


class UserInteractor:
    
    def __init__(
        self, 
        user_repository: UserRepository,
    ) -> None:
        
        self.user_repository = user_repository

    def get_user_info(
        self,
        user_id: str,
    ) -> UserModel:
        
        logger.info(f"Getting user info for user_id: {user_id}")
        
        user = self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            logger.error(f"User with id '{user_id}' not found")
            raise UserNotFoundError()
        
        return user
    