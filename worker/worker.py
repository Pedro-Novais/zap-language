from celery import Task
from celery.exceptions import Retry
from loguru import logger

from external.container import (
    app_celery,
    system_config,
    get_conversation_manager,
)

from core.shared.errors import (
    RetryWhitoutCountAttempt,
    RetryCountAttempt,
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
        conversation_manager.process_incoming_message(
            phone=phone, 
            message=message,
        )
        logger.info(f"Message from {phone} processed successfully.")
    
    except RetryCountAttempt as exc:
        raise self.retry(exc=exc)
    
    except RetryWhitoutCountAttempt as exc:
        raise self.retry(
            count_retries=False,
            countdown=config.timeout_to_message_lock_by_ai, 
        )
    
    except Retry:
        current_attempt = self.request.retries
        logger.warning(
            f"Rescheduling processing for {phone} "
            f"Current attempt: {current_attempt} of {self.max_retries}"
        )
        raise

    except Exception as exc:
        return
