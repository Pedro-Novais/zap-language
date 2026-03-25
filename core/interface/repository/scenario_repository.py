from abc import ABC, abstractmethod
from typing import Optional

from core.model import ScenarioModel


class ScenarioRepository(ABC):

    @abstractmethod
    def get_by_key(
        self, 
        key: str,
    ) -> Optional[ScenarioModel]:
        
        raise NotImplementedError()
