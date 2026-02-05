from abc import (
    ABC, 
    abstractmethod,
)


class EventPublisherService(ABC):

    @abstractmethod
    def notify_settings_changed(
        self,
        phone: str,
    ) -> None:
        
        raise NotImplementedError()
    