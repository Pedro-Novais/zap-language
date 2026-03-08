from abc import ABC, abstractmethod
from typing import Optional

from core.model import ConversationSessionModel


class ConversationSessionRepository(ABC):

    @abstractmethod
    def create_new_session(
        self,
        phone: str,
    ) -> ConversationSessionModel:
        
        raise NotImplementedError()

    @abstractmethod
    def get_last_session_by_phone(
        self, 
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_session_as_expired(
        self, 
        session_id: str,
    ) -> None:
        
        raise NotImplementedError()
