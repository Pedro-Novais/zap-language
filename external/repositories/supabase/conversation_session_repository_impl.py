from typing import Optional

from core.interface.repository import ConversationSessionRepository
from core.model import ConversationSessionModel


class ConversationSessionRepositoryImpl(ConversationSessionRepository):
    
    def create_new_session(
        self,
        phone: str,
    ) -> ConversationSessionModel:
        
        raise NotImplementedError()

    def get_last_session_by_phone(
        self, 
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        raise NotImplementedError()
    
    def set_session_as_expired(
        self, 
        session_id: str,
    ) -> None:
        
        raise NotImplementedError()
