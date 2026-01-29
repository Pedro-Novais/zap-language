from typing import List
from abc import (
    ABC, 
    abstractmethod,
)


class AITutorService(ABC):

    @abstractmethod
    def get_tutor_response(
        self, 
        history: List[str],
        message: str,
    ) -> str:
        
        raise NotImplementedError()