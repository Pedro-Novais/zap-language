from threading import Lock

from loguru import logger

from external.repositories import (
    UserRepositoryImpl,
    MessageHistoryRepositoryImpl,
)
from external.services import (
    redis_client,
    ZApiService,
    AITutorService,
)
from core.manager import ConversationManager
from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager

_ai_lock = Lock()


def _builder_manager() -> ConversationManager:
    
    user_repository = UserRepositoryImpl()
    history_repo = MessageHistoryRepositoryImpl()
    
    message_history_manager = MessageHistoryManager(
        redis_client=redis_client,
        history_repository=history_repo,
    )
    user_manager = UserManager(
        redis_client=redis_client,
        user_repository=user_repository,
    )
    
    zapi_service = ZApiService()
    ai_tutor_service = AITutorService()
    
    return ConversationManager(
        user_manager=user_manager,
        message_history_manager=message_history_manager,
        ai_tutor_service=ai_tutor_service, 
        whatsapp_service=zapi_service,
        redis_client=redis_client,
    )

manager = _builder_manager()


def message_processing_task(
    phone: str, 
    message: str,
) -> None:
    
    with _ai_lock:
        try:
            logger.info(f"🔨 [Worker] Processando para {phone}")
            manager.process_and_respond(
                phone=phone, 
                message_text=message,
            )

        except Exception as e:
            logger.error(f"Error processing message from number {phone}, erro: {e}")
