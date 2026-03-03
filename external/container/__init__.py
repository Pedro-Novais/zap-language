from external.container.instances import (
    get_conversation_manager,
    user_repository,
    history_repository,
    phone_verification_repository,
    study_settings_repository,
    whatsapp_service,
    ai_tutor_service,
    password_hasher_service,
    redis_service,
    system_config,
)
from external.container.celery import app_celery
