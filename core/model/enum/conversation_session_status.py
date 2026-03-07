from enum import StrEnum
    

class ConversationSessionsState(StrEnum):

    PRACTICING = "practicing"
    EXAM = "exam"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    AWAITING_DEFINITION = "awaiting_definition"
