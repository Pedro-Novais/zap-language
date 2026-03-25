from enum import StrEnum
    

class ConversationSessionsState(StrEnum):
    
    INITIALIZED = "initialized"
    EXAM = "exam"
    AWAITING_DEFINITION = "awaiting_definition"
    PRACTICING = "practicing"
    COMPLETED = "completed"
    CANCELLED_BY_USER = "cancelled_by_user"
    CANCELLED_BY_SYSTEM = "cancelled_by_system"
    EXPIRED = "expired"
    ERROR = "error"
