from abc import ABC, abstractmethod
from typing import Optional

from core.model import PhoneVerificationModel


class PhoneVerificationRepository(ABC):

    @abstractmethod
    def create_verification_code(
        self,
        user_id: str,
        phone_number: Optional[str],
        code: str,
        code_type: str = "PHONE",
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def get_verification_code_information(
        self,
        user_id: str,
        phone_number: Optional[str],
        code_type: str = "PHONE",
    ) -> Optional[PhoneVerificationModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_old_verification_code(
        self,
        user_id: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_attempts_in_verification_code(
        self,
        code_id: str,
        attempts: int,
    ) -> None:
        
        raise NotImplementedError()
