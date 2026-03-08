from abc import ABC, abstractmethod

from core.model import ConversationSessionModel


class ConversationHandler(ABC):
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def process_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> None:

        raise NotImplementedError()
    
    def __send_message(self) -> None:
        pass
