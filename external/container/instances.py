from external.repositories import (
    UserRepositoryImpl,
    MessageHistoryRepositoryImpl,
    PhoneVerificationRepositoryImpl,
    StudySettingsRepositoryImpl,
    SystemConfigRepositoryImpl,
)
from external.services import (
    ZApiService,
    AITutorService,
    RedisServiceImpl,
    BcryptPasswordHasherService,
)
from external.container.redis import redis_client

from core.manager import ConversationManager
from core.manager.services import UserService, MessageHistoryService
from core.manager.command import CommandHandler
from core.shared.model import SystemConfigModel


user_repository = UserRepositoryImpl()
history_repository = MessageHistoryRepositoryImpl()
phone_verification_repository = PhoneVerificationRepositoryImpl()
study_settings_repository = StudySettingsRepositoryImpl()
system_config_repository = SystemConfigRepositoryImpl()

system_config_model = SystemConfigModel(configs=system_config_repository.get_configurations())
system_config = system_config_model.get_system_config()

whatsapp_service = ZApiService()
ai_tutor_service = AITutorService()
password_hasher_service = BcryptPasswordHasherService()
redis_service = RedisServiceImpl(
    config=system_config.redis,
    redis_client=redis_client,
)

conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    
    global conversation_manager
    if conversation_manager is None:
        message_history_service = MessageHistoryService(
            config=system_config.history,
            redis_service=redis_service,
            history_repository=history_repository,
        )
        user_service = UserService(
            redis_service=redis_service,
            user_repository=user_repository,
        )
        
        command_handler = CommandHandler(
            user_service=user_service,
            message_history_service=message_history_service,
        )
        
        return ConversationManager(
            config=system_config.conversation,
            user_service=user_service,
            message_history_service=message_history_service,
            ai_tutor_service=ai_tutor_service, 
            whatsapp_service=whatsapp_service,
            command_handler=command_handler,
            redis_service=redis_service,
        )
    
    return conversation_manager
