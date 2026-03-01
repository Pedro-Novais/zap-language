from enum import StrEnum


class SystemConfigKey(StrEnum):
    CELERY = "celery"
    REDIS = "redis"
    CONVERSATION_MANAGER = "conversation_manager"
    HISTORY_MANAGER = "history_manager"
    