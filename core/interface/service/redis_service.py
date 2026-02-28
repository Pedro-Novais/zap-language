from typing import Optional
from abc import (
    ABC, 
    abstractmethod,
)


class RedisService(ABC):

    @abstractmethod
    def notify_settings_changed(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def has_lock_global_ia(
        self,
    ) -> bool:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_lock_global_ia(
        self,
        timeout,
    ) -> None:
        
        raise NotImplementedError()
    @abstractmethod
    def get_api_user_cached(
        self,
        user_id: str,
    ) -> Optional[str]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_api_user_cached(
        self,
        user_id: str,
    ) -> None:
        
        raise NotImplementedError()
    