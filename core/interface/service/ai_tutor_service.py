from typing import List, Optional, Dict, Any
from abc import (
    ABC, 
    abstractmethod,
)

from core.model import MessageHistoryModel


class AITutorService(ABC):

    @abstractmethod
    def get_tutor_response(
        self,
        message: str,
        instruction: str, 
        history: Optional[List[MessageHistoryModel]],
    ) -> str:
        
        raise NotImplementedError()