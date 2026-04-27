from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from core.model import UserModel


class UserRepository(ABC):

    @abstractmethod
    def get_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[UserModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_safe_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[UserModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def get_user_by_email(
        self, 
        email: str,
    ) -> Optional[UserModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_user_by_phone_number(
        self, 
        phone: str,
    ) -> Optional[UserModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def create(
        self, 
        email: str,
        name: str,
        password_hash: str,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def create_google_user(
        self,
        name: str,
        email: str,
        google_id: str,
        password_hash: str,
        last_login: datetime,
    ) -> UserModel:

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
    
    @abstractmethod
    def update_password(
        self, 
        user_id: str,
        new_password_hash: str,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def update_google_login(
        self,
        user_id: str,
        google_id: str,
        last_login: datetime,
    ) -> UserModel:

        raise NotImplementedError()

    @abstractmethod
    def update_is_valid(
        self,
        user_id: str,
        is_valid: bool,
    ) -> None:

        raise NotImplementedError()
