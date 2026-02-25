from enum import StrEnum


class SystemConfigKey(StrEnum):
    AI_MODEL_FALLBACK = "ai_model_fallback"
    WORKER_RETRY_SETTINGS = "worker_retry_settings"
    MAINTENANCE_MODE = "maintenance_mode"
    PROMPT_VERSION = "prompt_version"
    RATE_LIMIT_THRESHOLD = "rate_limit_threshold"
    