from datetime import (
    datetime, 
    timezone, 
    timedelta,
)
from typing import Optional

from loguru import logger

from core.interface.repository import ConversationSessionRepository
from core.interface.service import RedisService
from core.model import ConversationSessionModel
from core.model.enum import ConversationSessionsState
from core.model.enum.conversation_session_type import ConversationSessionsType


class ConversationSessionService:
   
    def __init__(
        self, 
        redis_service: RedisService,
        conversation_session_repo: ConversationSessionRepository, 
    ) -> None:
        
        self.redis_service = redis_service
        self.conversation_session_repo = conversation_session_repo

    def get_last_session(
        self,
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        session = self.__get_last_session(phone=phone)
        if not session:
            return None
        
        session_is_valid = self.__verify_if_last_session_is_valid(
            phone=phone,
            session=session,
        )
        if session_is_valid:
            return session
        
        return None
        
    def create_new_session(
        self,
        phone: str,
    ) -> ConversationSessionModel:
        
        logger.info(f"Creating new context session for {phone}")
        
        session = self.conversation_session_repo.create_new_session(phone=phone)
        self.redis_service.set_conversation_session(
            phone=phone,
            session=session.model_dump_json(),
        )
        return session
    
    def set_start_session_scenario(
        self, 
        phone: str,
        session: ConversationSessionModel,
        scenario: Optional[str] = None,
    ) -> None:
        
        self.redis_service.delete_conversation_session(phone=phone)
        logger.info("Setting start scenario session, updating context and session status")
        session = self.conversation_session_repo.update_session(
            session_id=session.id,
            scenario=scenario,
            session_type=ConversationSessionsType.SCENARIO,
            status=ConversationSessionsState.PRACTICING,
        )
        self.redis_service.set_conversation_session(
            phone=phone,
            session=session.model_dump_json(),
        )
        return session
    
    def set_start_session_free_talk(
        self, 
        phone: str,
        session: ConversationSessionModel,
        context_summary: Optional[str] = None,
        context_description: Optional[str] = None,
    ) -> ConversationSessionModel:
        
        self.redis_service.delete_conversation_session(phone=phone)
        logger.info("Setting start session for free talk, updating context and session status")
        session = self.conversation_session_repo.update_session(
            session_id=session.id,
            context_summary=context_summary,
            session_type=ConversationSessionsType.FREE_TALK,
            status=ConversationSessionsState.PRACTICING,
            context_description=context_description,
        )
        self.redis_service.set_conversation_session(
            phone=phone,
            session=session.model_dump_json(),
        )
        return session
    
    def set_session_state(
        self, 
        phone: str,
        session_id: str,
        state: ConversationSessionsState,
    ) -> None:
        
        self.redis_service.delete_conversation_session(phone=phone)
        session_model = self.conversation_session_repo.set_session_state(
            session_id=session_id,
            state=state,
        )
        self.redis_service.set_conversation_session(
            phone=phone,
            session=session_model.model_dump_json(),
        )
    
    def __get_last_session(
        self, 
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        logger.info(f"Getting last session for {phone}")
        session_cached = self.redis_service.get_conversation_session(phone=phone)
        if session_cached:
            logger.info(f"Cache hit to {phone}")
            return ConversationSessionModel.model_validate_json(session_cached)
        
        logger.info(f"Cache miss to {phone}. Getting from database")
        session_from_db = self.conversation_session_repo.get_last_session_by_phone(phone=phone)
        return session_from_db
    
    def __verify_if_last_session_is_valid(
        self, 
        phone: str,
        session: ConversationSessionModel,
    ) -> bool:
        
        if self.__verify_if_session_is_expired(session=session):
            logger.warning(f"Last Session for phone: {phone} is expired")
            self.conversation_session_repo.set_session_as_expired(session_id=session.id)
            return False

        valid_status = [
            ConversationSessionsState.PRACTICING,
            ConversationSessionsState.AWAITING_DEFINITION,
            ConversationSessionsState.INITIALIZED,
        ]

        if session.status in valid_status:
            logger.info(f"Last Session is valid for phone: {phone}, status: {session.status}")
            return True

        logger.warning(f"Session for is invalid for phone: {phone}, status: {session.status}")
        return False
    
    @staticmethod
    def __verify_if_session_is_expired(
        session: ConversationSessionModel,
    ) -> bool:
        
        now = datetime.now(timezone.utc)
        diff = now - session.created_at
        return diff > timedelta(hours=12)
