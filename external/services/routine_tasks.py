import logging
from external.repositories import UserRepositoryImpl
from external.services import (
    celery,
    ZApiService,
    AITutorService,
)
from core.interactor.conversation import PROMPT_MAP
from core.manager import ConversationManager

logger = logging.getLogger("WorkerService")


user_repository = UserRepositoryImpl()
# history_repo = MessageHistoryRepositoryImpl()
zapi_service = ZApiService()
ai_tutor_service = AITutorService()

manager = ConversationManager(
    user_repository=user_repository, 
    ai_tutor_service=ai_tutor_service, 
    whatsapp_service=zapi_service,
)

logger = logging.getLogger("WorkerService")


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