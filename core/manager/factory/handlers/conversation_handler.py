from abc import ABC, abstractmethod

from loguru import logger
from typing import Optional

from core.interface.service import RedisService
from core.model import ConversationSessionModel
from core.model.enum.conversation_session_state import ConversationSessionsState
from core.model.user_model import UserModel
from core.shared.errors import (
    GlobalIALockError,
    SessionActiveError,
    SessionStateInvalidError,
)


class ConversationHandler(ABC):

    @abstractmethod
    def reply_message(
        self, 
        user: UserModel,
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> str:

        raise NotImplementedError()
        

class StudySessionMixin(ABC):

    @staticmethod
    def _check_ia_lock(
        phone: str,
        redis_service: RedisService,
    ) -> None:
        
        if redis_service.has_lock_global_ia():
            logger.warning(f"Global IA lock active for {phone}")
            raise GlobalIALockError()
    
    @staticmethod
    def _verify_session_interrupt(
        session: ConversationSessionModel,
    ) -> None:
        
        if session.status == ConversationSessionsState.PRACTICING:
            logger.warning(f"Already exist a running session")
            raise SessionActiveError()

        valid_states = [
            ConversationSessionsState.INITIALIZED, 
            ConversationSessionsState.AWAITING_DEFINITION
        ]
        if session.status not in valid_states:
            logger.error(f"Session state is invalid, user state: {session.status}")
            raise SessionStateInvalidError()
        
        return
    

class CommandHandlerMixin(ABC):
    
    @abstractmethod
    def is_command(
        self,
        message: str,
    ) -> bool:
        
        raise NotImplementedError()
    
    @staticmethod
    def _extract_key_after_command(
        message: str
    ) -> Optional[str]:
        
        try:
            parts = message.strip().split(maxsplit=1)
            if len(parts) > 1:
                key = parts[1].strip().lower()
                
                if len(key) >= 2:
                    logger.info(f"Extracted key: {key}")
                    return key
            
            logger.info("Extracted key: None")
            return None
            
        except Exception:
            logger.error(f"Error extracting key")
            return None
