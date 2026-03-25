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
        session_id: str,
        messages_from_the_last_hours: int = 5,
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def insert_messages(
        self,
        user_id: str,
        session_id: str,
        messages: List[MessageHistoryModel],
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def invalidate_messages_by_phone(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def invalidate_messages_by_session(
        self,
        session_id: str,
    ) -> None:
        
        raise NotImplementedError()
