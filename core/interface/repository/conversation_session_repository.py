from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from core.model import (
    ConversationSessionModel,
    ScenarioModel,
)
from core.model.enum import (
    ConversationSessionsType,
    ConversationSessionsState,
)


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
    
    @abstractmethod
    def set_session_state(
        self, 
        session_id: str,
        state: ConversationSessionsState,
    ) -> ConversationSessionModel:
        
        raise NotImplementedError()
    
    @abstractmethod
    def update_session(
        self, 
        session_id: UUID,
        scenario: Optional[ScenarioModel] = None,
        status: Optional[ConversationSessionsState] = None,
        session_type: Optional[ConversationSessionsType] = None,
        context_summary: Optional[str] = None,
        context_description: Optional[str] = None,
    ) -> ConversationSessionModel:
        
        raise NotImplementedError()
