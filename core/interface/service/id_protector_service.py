from abc import ABC, abstractmethod

class IDProtectorService(ABC):
    
    @abstractmethod
    def encrypt(
        self, 
        real_id: str,
    ) -> str:
        
        raise NotImplementedError()

    @abstractmethod
    def decrypt(
        self, 
        encrypted_id: str,
    ) -> str:
        
        raise NotImplementedError()