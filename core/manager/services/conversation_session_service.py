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


class ConversationSessionService:
   
    def __init__(
        self, 
        redis_service: RedisService,
        conversation_session_repo: ConversationSessionRepository, 
    ) -> None:
        
        self.redis_service = redis_service
        self.conversation_session_repo = conversation_session_repo

    def get_current_session(
        self,
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        session = self.__get_last_session(phone=phone)
        if not session:
            return None
        
        if self.__verify_if_current_session_is_valid(session=session):
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
    
    def __verify_if_current_session_is_valid(
        self, 
        session: ConversationSessionModel,
    ) -> bool:
        
        if self.__verify_if_session_is_expired(session=session):
            logger.warning(f"Last Session for {session.phone} is expired")
            self.conversation_session_repo.set_session_as_expired(session_id=session.id)
            return False

        valid_status = [
            ConversationSessionsState.AWAITING_DEFINITION,
            ConversationSessionsState.PRACTICING,
            ConversationSessionsState.EXAM,
            ConversationSessionsState.UNDEFINED,
        ]

        if session.status in valid_status:
            logger.info(f"Last Session for {session.phone} is valid, status: {session.status}")
            return True

        logger.info(f"Session for {session.phone} is invalid, status: {session.status}")
        return False
    
    @staticmethod
    def __verify_if_session_is_expired(
        session: ConversationSessionModel,
    ) -> bool:
        
        now = datetime.now(timezone.utc)
        diff = now - session.created_at
        return diff > timedelta(hours=5)
