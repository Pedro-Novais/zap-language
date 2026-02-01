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
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def insert_messages(
        self,
        user_id: str,
        messages: List[MessageHistoryModel],
    ) -> List[MessageHistoryModel]:
        
        raise NotImplementedError()
