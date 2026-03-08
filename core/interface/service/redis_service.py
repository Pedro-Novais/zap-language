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
    def has_update_to_user_profile(
        self,
        phone: str,
    ) -> bool:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_update_user_profile(
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
        timeout: Optional[int] = None,
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

    @abstractmethod
    def user_is_banned(
        self,
        phone: str,
    ) -> bool:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_current_processing_phone(
        self,
        phone: str,
        timeout: int,
    ) -> None:
        
        raise NotImplementedError()
        
    @abstractmethod
    def user_beeing_processed(
        self,
        phone: str,
    ) -> bool:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_processing_phone(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def ban_phone(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_user_profile(
        self,
        phone: str,
    ) -> Optional[str]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_user_profile(
        self,
        phone: str,
        user_profile: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_user_profile(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_message_history(
        self,
        phone: str,
    ) -> Optional[str]:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_message_history(
        self,
        phone: str,
        message: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def delete_message_history(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def api_user_cached(
        self,
        user_id: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def set_conversation_session(
        self,
        phone: str,
        session: str,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def get_conversation_session(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    