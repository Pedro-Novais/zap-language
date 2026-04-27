from abc import ABC, abstractmethod
from typing import Optional

from core.model import PhoneVerificationModel
from core.model.enum.verification_code_type import VerificationCodeType


class PhoneVerificationRepository(ABC):

    @abstractmethod
    def create_verification_code(
        self,
        user_id: str,
        value: Optional[str],
        code: str,
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def get_verification_code_information(
        self,
        user_id: str,
        value: Optional[str],
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> Optional[PhoneVerificationModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_old_verification_code(
        self,
        user_id: str,
        code_type: VerificationCodeType | None = None,
    ) -> None:
        """
        Remove códigos antigos do usuário. Se code_type for informado, remove apenas daquele tipo.
        """
        raise NotImplementedError()
    
    @abstractmethod
    def set_attempts_in_verification_code(
        self,
        code_id: str,
        attempts: int,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def get_verification_by_code(
        self,
        code: str,
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> Optional[PhoneVerificationModel]:
        
        raise NotImplementedError()
