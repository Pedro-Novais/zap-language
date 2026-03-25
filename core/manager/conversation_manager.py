from loguru import logger

from core.shared.model import ConversationManagerConfig
from core.shared.errors import ConversationManagerError
from core.manager.services import (
    UserService, 
    MessageHistoryService,
    ConversationSessionService,
    ScenarioService,
)
from core.interface.service import (
    AITutorService,
    WhatsappService,
    RedisService,
)
from core.manager.factory import ConversationFactory


class ConversationManager:

    def __init__(
        self,
        config: ConversationManagerConfig,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        redis_service: RedisService,
        user_service: UserService,
        message_history_service: MessageHistoryService,
        conversation_session_service: ConversationSessionService,
        scenario_service: ScenarioService,
    ) -> None:
        
        self.conversation_factory = ConversationFactory(
            config=config,
            ai_tutor_service=ai_tutor_service,
            whatsapp_service=whatsapp_service,
            redis_service=redis_service,
            user_service=user_service,
            message_history_service=message_history_service,
            conversation_session_service=conversation_session_service,
            scenario_service=scenario_service,
        )
    
    def process_incoming_message(
        self, 
        phone: str, 
        message: str,
    ) -> None:
        
        try:
            user = self.conversation_factory.validate_user(phone=phone)
            session = self.conversation_factory.get_session(
                user=user,
                phone=phone,
            )
            message_handler = self.conversation_factory.get_handler(
                message=message,
                session=session, 
            )
            reply_message = message_handler.reply_message(
                user=user,
                phone=phone, 
                message=message,
                session=session,
            )
            self.conversation_factory.send_message(
                phone=phone, 
                message=reply_message,
            )
            self.conversation_factory.finalize_message_processing(phone=phone)
        
        except ConversationManagerError as ex:
            self.conversation_factory.handle_error(
                phone=phone, 
                session=session,
                error=ex,
            )
            self.conversation_factory.finalize_message_processing(phone=phone)
        
        except Exception:
            logger.error(f"Unexpected error processing message from {phone}")
            self.conversation_factory.finalize_message_processing(phone=phone)
            raise
