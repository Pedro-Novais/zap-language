from typing import List
from abc import (
    ABC, 
    abstractmethod,
)

class ZapiService(ABC):

    @abstractmethod
    def send_text(
        self, 
        phone: str, 
        message: str,
    ) -> None:
        
        raise NotImplementedError()