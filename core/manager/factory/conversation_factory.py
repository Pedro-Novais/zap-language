from loguru import logger

from external.services.ai_tutor_service import AITutorService

from core.manager.factory.handlers.conversation_handler import ConversationHandler
from core.manager.factory.handlers.free_talk_handler import FreeTalkHandler
from core.manager.factory.handlers.scenario_handler import ScenarioHandler
from core.manager.factory.handlers.command_handler import CommandHandler
from core.manager.factory.handlers.undefined_handler import UndefinedHandler

from core.interface.service.redis_service import RedisService
from core.interface.service.whatsapp_service import WhatsappService
from core.manager.services.conversation_session_service import ConversationSessionService
from core.manager.builder.instruction_builder import InstructionBuilder
from core.manager.services.message_history_service import MessageHistoryService
from core.manager.services.user_service import UserService
from core.model import ConversationSessionModel
from core.model.enum import ConversationSessionsType
from core.shared.model.system_configs_model import ConversationManagerConfig


class ConversationFactory:
    def __init__(
        self,
        config: ConversationManagerConfig,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        redis_service: RedisService,
        user_service: UserService,
        message_history_service: MessageHistoryService,
        conversation_session_service: ConversationSessionService,
    ) -> None:
        
        self.config = config

        self.user_service = user_service
        self.message_history_service = message_history_service
        self.conversation_session_service = conversation_session_service
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service
        self.redis_service = redis_service

        self.instruction_builder = InstructionBuilder()
        
        self.free_talk_handler = FreeTalkHandler(
            ai_tutor_service=self.ai_tutor_service,
            whatsapp_service=self.whatsapp_service,
            redis_service=self.redis_service,
            user_service=self.user_service,
            message_history_service=self.message_history_service,
        )
        self.scenario_handler = ScenarioHandler()
        self.command_handler = CommandHandler(
            user_service=self.user_service,
            message_history_service=self.message_history_service,
        )
        self.undefined_handler = UndefinedHandler()
    
    def get_current_session(
        self, 
        phone: str,
    ) -> ConversationSessionModel:
        
        current_session = self.conversation_session_service.get_current_session(phone=phone)
        if current_session:
            return current_session
        
        return self.conversation_session_service.create_new_session(phone=phone)
    
    def get_handler(
        self, 
        message: str,
        session: ConversationSessionModel,
    ) -> ConversationHandler:
        
        logger.info(f"Getting handler for session type: {session.session_type.value}")
        
        is_command_message = self.command_handler.is_command(user_message=message)
        if is_command_message:
            logger.info("Getting command handler")
            return self.command_handler
            
        if session.session_type == ConversationSessionsType.FREE_TALK:
            logger.info("Getting free talk handler")
            return self.free_talk_handler
        
        if session.session_type == ConversationSessionsType.SCENARIO:
            logger.info("Getting scenario handler")
            return self.scenario_handler

        if session.session_type == ConversationSessionsType.UNDEFINED:
            logger.info("Getting undefined handler")
            return self.undefined_handler
        
        logger.warning("Session type not mapped, returning undefined handler")
        return self.undefined_handler
    