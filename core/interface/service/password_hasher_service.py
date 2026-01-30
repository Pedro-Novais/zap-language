from abc import ABC, abstractmethod


class PasswordHasherService(ABC):

    @abstractmethod
    def hash(
        self, 
        password: str,
    ) -> str:
        pass

    @abstractmethod
    def verify(
        self,
        password_sended: str,
        password_saved: str,
    ) -> bool:
        pass
