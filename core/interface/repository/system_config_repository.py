from typing import Dict
from abc import ABC, abstractmethod

from core.model import SystemConfigModel


class SystemConfigRepository(ABC):

    @abstractmethod
    def get(
        self,
    ) -> Dict[str, SystemConfigModel]:
        
        raise NotImplementedError()
