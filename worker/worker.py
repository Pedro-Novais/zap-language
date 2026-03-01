from celery import Task
from celery.exceptions import Retry
from loguru import logger

from external.container import (
    app_celery,
    redis_service,
    system_config,
    get_conversation_manager,
)

from core.shared.errors import (
    AiWithQuotaLimitReachedError, 
    ErrorSendingMessageToWhatsapp,
)
from core.shared.model import CeleryConfig


config: CeleryConfig = system_config.celery

conversation_manager = get_conversation_manager()         
                
@app_celery.task(
    bind=True,                                     # Permite acessar o contexto da tarefa, como tentativas e tempo de espera
    max_retries=config.max_retry,                  # Número máximo de tentativas
    retry_backoff=config.retry_backoff,            # Substitui seu _update_time_to_sleep_on_error
    retry_backoff_max=config.retry_backoff_max,    # Tempo máximo de espera (10 min)
    retry_jitter=config.retry_jitter,              # Evita que muitos workers tentem ao mesmo tempo
)
def process_whatsapp_message(
    self: Task, 
    phone: str, 
    message: str,
) -> None:
    
    try:    
        logger.info(f"Processing message for {phone}")
        
        can_process = conversation_manager.can_process_message(phone=phone)
        if not can_process:
            logger.warning(f"Message from {phone} can't be processed. Ignoring message")
            return
        
        conversation_manager.invalidate_cache_if_user_has_been_modified(phone=phone)
        
        if conversation_manager.message_is_command(message_text=message):
            logger.info(f"Message from {phone} is a command. Responsing to command")
            conversation_manager.respond_to_command(
                phone=phone, 
                message_text=message,
            )
        else:
            if redis_service.has_lock_global_ia():
                logger.warning(f"Global IA lock is active. Skipping message for {phone} to try again later.")
                raise self.retry(
                    countdown=config.timeout_to_message_lock_by_ai, 
                    count_retries=False,
                )
            
            logger.info("Message from {phone} is study message. Getting tutor response")
            conversation_manager.respond_user_with_tutor_message(
                phone=phone, 
                message_text=message,
            )
        
        logger.info(f"Message from {phone} processed successfully.")
        redis_service.set_lock_global_ia()
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
            f"Rescheduling processing for {phone} "
            f"Current attempt: {current_attempt} of {self.max_retries}"
        )
        raise

    except Exception as exc:
        logger.error(f"Unexpected error processing message from {phone}: {str(exc)}", exc_info=True)
        redis_service.delete_processing_phone(phone=phone)
        return
