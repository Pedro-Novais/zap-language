from external.repositories import (
    UserRepositoryImpl,
    MessageHistoryRepositoryImpl,
    PhoneVerificationRepositoryImpl,
    StudySettingsRepositoryImpl,
)
from external.services import (
    ZApiService,
    AITutorService,
    RedisServiceImpl,
    BcryptPasswordHasherService,
)
from external.container.redis import redis_client

from core.manager import ConversationManager
from core.manager.user_manager import UserManager
from core.manager.message_history_manager import MessageHistoryManager
from core.manager.command import CommandHandler


user_repository = UserRepositoryImpl()
history_repository = MessageHistoryRepositoryImpl()
phone_verification_repository = PhoneVerificationRepositoryImpl()
study_settings_repository = StudySettingsRepositoryImpl()

whatsapp_service = ZApiService()
ai_tutor_service = AITutorService()
password_hasher_service = BcryptPasswordHasherService()
redis_service = RedisServiceImpl(redis_client=redis_client)

conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    
    global conversation_manager
    if conversation_manager is None:
        message_history_manager = MessageHistoryManager(
            redis_client=redis_client,
            history_repository=history_repository,
        )
        user_manager = UserManager(
            redis_client=redis_client,
            user_repository=user_repository,
        )
        
        command_handler = CommandHandler(
            user_manager=user_manager,
            message_history_manager=message_history_manager,
        )
        
        return ConversationManager(
            user_manager=user_manager,
            message_history_manager=message_history_manager,
            ai_tutor_service=ai_tutor_service, 
            whatsapp_service=whatsapp_service,
            redis_client=redis_client,
            command_handler=command_handler,
        )
    
    return conversation_manager
