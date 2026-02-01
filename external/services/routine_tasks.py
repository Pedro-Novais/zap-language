from loguru import logger

from external.repositories import (
    UserRepositoryImpl,
    MessageHistoryRepositoryImpl,
)
from external.services import (
    celery,
    redis_client,
    ZApiService,
    AITutorService,
)
from core.manager import ConversationManager
from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager


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


@celery.task(
    bind=True, 
    max_retries=3,
)
def message_processing_task(
    self,
    phone: str, 
    user_message: str,
) -> None:
    
    logger.info(f"🔨 [Worker] Processando para {phone}")
    
    try:
        manager.process_and_respond(
            phone=phone, 
            message_text=user_message,
        )

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        self.retry(exc=e, countdown=5)
