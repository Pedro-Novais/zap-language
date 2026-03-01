from celery import Task
from celery.exceptions import Retry
from loguru import logger

from external.container import (
    app_celery,
    redis_service,
    get_conversation_manager,
)

from core.shared.errors import (
    AiWithQuotaLimitReachedError, 
    ErrorSendingMessageToWhatsapp,
)


conversation_manager = get_conversation_manager()         
                
@app_celery.task(
    bind=True,                # Permite acessar o contexto da tarefa, como tentativas e tempo de espera
    max_retries=3,            # Número máximo de tentativas
    retry_backoff=True,       # Substitui seu _update_time_to_sleep_on_error
    retry_backoff_max=600,    # Tempo máximo de espera (10 min)
    retry_jitter=True,        # Evita que muitos workers tentem ao mesmo tempo
)
def process_whatsapp_message(
    self: Task, 
    phone: str, 
    message: str,
) -> None:
    
    try:    
        if redis_service.has_lock_global_ia():
            logger.warning(f"Global IA lock is active. Skipping message processing for {phone} to try again later.")
            raise self.retry(
                countdown=15, 
                count_retries=False,
            )
         
        logger.info(f"Processing message for {phone}")
        
        is_valid = conversation_manager.process_message(phone=phone)
        if not is_valid:
            logger.warning(f"Message from {phone} not processed due to restrictions or AI health.")
            return
            
        conversation_manager.reply_user(
            phone=phone, 
            message_text=message,
        )
        
        logger.info(f"Message from {phone} processed successfully.")
        redis_service.set_lock_global_ia(timeout=15)
        redis_service.delete_processing_phone(phone=phone)
    
    except AiWithQuotaLimitReachedError as exc:
        timeout = 30
        logger.error(f"AI quota limit reached, putting AI to sleep for {timeout} seconds")
        redis_service.set_lock_global_ia(timeout=timeout)
        raise self.retry(exc=exc)
        
    except ErrorSendingMessageToWhatsapp as exc:
        logger.error(f"Failed to send message to {phone} by whatsapp: {exc}")
        raise self.retry(exc=exc)
    
    except Retry:
        current_attempt = self.request.retries
        logger.warning(
            f"Rescheduling processing for {phone}"
            f"Current attempt: {current_attempt} of {self.max_retries}"
        )
        raise

    except Exception as exc:
        logger.error(f"Fatal error processing message from {phone}, we will not try again.")
        redis_service.delete_processing_phone(phone=phone)
        return
