from loguru import logger

from external.services.ai_tutor_service import AITutorService

from core.manager.factory.handlers.conversation_handler import ConversationHandler
from core.manager.factory.handlers.free_talk_handler import FreeTalkHandler
from core.manager.factory.handlers.scenario_handler import ScenarioHandler
from core.manager.factory.handlers.command_handler import CommandHandler
from core.manager.factory.handlers.undefined_handler import UndefinedHandler
from core.manager.services import (
    ScenarioService,
    UserService, 
    MessageHistoryService, 
    ConversationSessionService,
)

from core.interface.service.redis_service import RedisService
from core.interface.service.whatsapp_service import WhatsappService
from core.model import ConversationSessionModel, UserModel
from core.shared.errors import (
    UserBannedError,
    AiWithQuotaLimitReachedError,
    ConversationManagerError, 
    GlobalIALockError, 
    SessionActiveError,
    SessionStateInvalidError,
    ErrorSendingMessageToWhatsapp,
    RetryCountAttempt,
    RetryWhitoutCountAttempt,
)
from core.model.enum import ConversationSessionsType, ConversationSessionsState
from core.shared.model.system_configs_model import ConversationManagerConfig
from core.shared.model.answers import GeneralAnswers


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
        scenario_service: ScenarioService,
    ) -> None:
        
        self.config = config

        self.user_service = user_service
        self.message_history_service = message_history_service
        self.conversation_session_service = conversation_session_service
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service
        self.redis_service = redis_service
        
        self.free_talk_handler = FreeTalkHandler(
            ai_tutor_service=self.ai_tutor_service,
            redis_service=self.redis_service,
            user_service=self.user_service,
            message_history_service=self.message_history_service,
            session_service=self.conversation_session_service,
        )
        self.scenario_handler = ScenarioHandler(
            ai_tutor_service=self.ai_tutor_service,
            redis_service=self.redis_service,
            message_history_service=self.message_history_service,
            session_service=self.conversation_session_service,
            scenario_service=scenario_service,
        )
        self.command_handler = CommandHandler(
            user_service=self.user_service,
            session_service=self.conversation_session_service,
            message_history_service=self.message_history_service, 
        )
        self.undefined_handler = UndefinedHandler(
            whatsapp_service=self.whatsapp_service,
            redis_service=self.redis_service,
            user_service=self.user_service,
            session_service=self.conversation_session_service,
        )
    
    def get_session(
        self, 
        phone: str,
        user: UserModel
    ) -> ConversationSessionModel:
        
        current_session = self.conversation_session_service.get_last_session(phone=phone)
        if current_session:
            return current_session
        
        return self.conversation_session_service.create_new_session(phone=phone)
    
    def get_handler(
        self, 
        message: str,
        session: ConversationSessionModel,
    ) -> ConversationHandler:
        
        logger.info(f"Getting handler for session type: {session.session_type.value}")
        
        is_command_message = self.command_handler.is_command(message=message)
        is_scenario_command = self.scenario_handler.is_command(message=message)
        is_free_talk_command = self.free_talk_handler.is_command(message=message)
        if is_scenario_command:
            return self.__get_scenario_handler()
        
        if is_free_talk_command:
            return self.__get_free_talk_handler()
        
        if is_command_message:
            return self.__get_command_handler()
    
        session_type = session.session_type
        if session_type == ConversationSessionsType.UNDEFINED:    
            return self.__get_undefined_handler()
            
        if session_type == ConversationSessionsType.FREE_TALK: 
            return self.__get_free_talk_handler()
        
        if session_type == ConversationSessionsType.SCENARIO:
            return self.__get_scenario_handler()
        
        logger.warning("Session type not mapped, returning undefined handler")
        return self.__get_undefined_handler()
    
    def send_message(
        self,
        phone: str,
        message: str,
    ) -> None:
        
        self.whatsapp_service.send_text(
            phone=phone, 
            message=message,
        )

    def finalize_message_processing(
        self, 
        phone: str,
        is_command_message: bool = True,
    ) -> None:
        
        logger.info(f"Removing phone: {phone} from processing queue")
        self.redis_service.delete_processing_phone(phone=phone)
        if not is_command_message:
            self.redis_service.set_lock_global_ia()
            
    def handle_error(
        self, 
        phone: str, 
        session: ConversationSessionModel,
        error: ConversationManagerError,
    ) -> None:
        
        message = None
        if isinstance(error, UserBannedError):
            return
        
        if isinstance(error, SessionActiveError):
            message = GeneralAnswers.SESSION_ALREADY_RUNNING_CLOSE_SESSION_FIRST
        
        if isinstance(error, SessionStateInvalidError):
            self.conversation_session_service.set_session_state(
                phone=phone,
                session_id=session.id,
                state=ConversationSessionsState.ERROR,
            )
            raise RetryWhitoutCountAttempt()
        
        if isinstance(error, GlobalIALockError):
            logger.warning(f"Global IA lock error")
            raise RetryWhitoutCountAttempt()
        
        if isinstance(error, ErrorSendingMessageToWhatsapp):
            logger.error(f"Failed to send message to {phone} by whatsapp")
            raise RetryCountAttempt()
        
        if isinstance(error, AiWithQuotaLimitReachedError):
            logger.warning(f"AI quota limit reached")
            self.redis_service.set_lock_global_ia(timeout=30)
            raise RetryWhitoutCountAttempt()
        
        self.send_message(
            phone=phone, 
            message=message,
        )

    def validate_user(
        self,
        phone: str,
    ) -> UserModel:
        
        if self.redis_service.user_is_banned(phone=phone):
            logger.warning(f"User {phone} is currently banned. Ignoring message.")
            raise UserBannedError()
        
        user = self.user_service.get_user_profile(phone=phone)
        if not user:
            logger.error(f"User not found or whatsapp not enabled, adding to blacklist: {phone}")
            self.__ban_user(phone=phone)
            return
        
        self.__invalidate_cache_if_user_has_been_modified(phone=phone)
        return user

    def __invalidate_cache_if_user_has_been_modified(
        self, 
        phone: str,
    ) -> None:

        if self.redis_service.has_update_to_user_profile(phone=phone):
            self.user_service.invalidate_user_cache(phone=phone)
            self.redis_service.delete_update_user_profile(phone=phone)
            self.message_history_service.clear_message_history_for_user(phone=phone)
            
    def __ban_user(
        self, 
        phone: str,
        message: str = "Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas.",
    ) -> None:

        logger.warning(f"Banning phone {phone}.")
        self.redis_service.ban_phone(phone=phone)
        if self.config.notify_user_when_banned:
            logger.info(f"Notifying phone: {phone} that it has been banned")
            self.whatsapp_service.send_text(
                phone=phone, 
                message=message,
            )
        
        raise UserBannedError()
    
    def __get_scenario_handler(self) -> ScenarioHandler:
        logger.info("Getting scenario handler")
        return self.scenario_handler
    
    def __get_free_talk_handler(self) -> FreeTalkHandler:
        logger.info("Getting free talk handler")
        return self.free_talk_handler
    
    def __get_undefined_handler(self) -> UndefinedHandler:
        logger.info("Getting undefined handler")
        return self.undefined_handler
    
    def __get_command_handler(self) -> CommandHandler:
        logger.info("Getting command handler")
        return self.command_handler
    