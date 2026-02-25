from abc import (
    ABC, 
    abstractmethod,
)
from typing import List

from core.model import MessageHistoryModel


class MessageHistoryRepository(ABC):

    @abstractmethod
    def get_messages(
        self,
        user_id: str,
        limit: int,
        messages_from_the_last_hours: int = 5,
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def insert_messages(
        self,
        user_id: str,
        messages: List[MessageHistoryModel],
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def invalidate_messages(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
