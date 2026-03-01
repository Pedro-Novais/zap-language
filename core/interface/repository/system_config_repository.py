from typing import Dict
from abc import ABC, abstractmethod


class SystemConfigRepository(ABC):

    @abstractmethod
    def get_configurations(
        self,
    ) -> Dict[str, str]:
        
        raise NotImplementedError()
