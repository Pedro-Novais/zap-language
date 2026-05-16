from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class PaymentService(ABC):

    @abstractmethod
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
    ) -> tuple[str, Optional[str], Optional[datetime]]:
        raise NotImplementedError()

    @abstractmethod
    def create_customer(
        self,
        user_id: str,
        name: str,
        email: str,
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    def cancel_subscription(
        self,
        user_id: str,
        subscription_id: str,
    ) -> None:
        raise NotImplementedError()
