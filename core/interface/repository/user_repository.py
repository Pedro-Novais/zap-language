from abc import ABC, abstractmethod
from typing import Optional

from external.database.models._User import User

class UserRepository(ABC):

    @abstractmethod
    def get_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[User]:
        
        raise NotImplementedError()

    def get_user_by_email(
        self, 
        email: str,
    ) -> Optional[User]:
        
        raise NotImplementedError()

    @abstractmethod
    def create(
        self, 
        email: str,
        name: str,
        password_hash: str,
    ) -> Optional[User]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_phone_number_by_user_id(
        self, 
        user_id: str,
    ) -> Optional[str]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def insert_phone_number_by_user_id(
        self, 
        user_id: str,
        phone_number: str,
    ) -> None:
        
        raise NotImplementedError()
