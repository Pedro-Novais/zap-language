from loguru import logger

from core.interface.service import (
    WhatsappService,
    RedisService,
)
from core.manager.factory.handlers import ConversationHandler
from core.model import (
    UserModel,
    ConversationSessionModel,
)
from core.manager.services import (
    UserService,
    ConversationSessionService,
)
from core.model.enum import ConversationSessionsState
from core.shared.model.answers import UndefinedAnswers



class UndefinedHandler(ConversationHandler):

    def __init__(
        self,
        whatsapp_service: WhatsappService,
        redis_service: RedisService,
        user_service: UserService,
        session_service: ConversationSessionService,
    ) -> None:
        
        self.whatsapp_service = whatsapp_service
        self.redis_service = redis_service
        self.user_service = user_service
        self.session_service = session_service
    
    def reply_message(
        self, 
        user: UserModel,
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> str:
        
        logger.info("Handling undefined session")
        
        if session.status == ConversationSessionsState.INITIALIZED:
            self.session_service.set_session_state(
                phone=phone,
                session_id=session.id,
                state=ConversationSessionsState.AWAITING_DEFINITION,
            )
            return UndefinedAnswers.SESSION_STARTED
        
        if session.status == ConversationSessionsState.AWAITING_DEFINITION:
            return UndefinedAnswers.SESSION_STARTED
        
        logger.error(f"Session not mapped to undefined handler, session status: {session.status}")
        raise NotImplementedError()
    