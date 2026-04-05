from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from core.model import SubscriptionModel


class SubscriptionRepository(ABC):

    @abstractmethod
    def get_active_by_user_id(self, user_id: str) -> Optional[SubscriptionModel]:
        raise NotImplementedError()

    @abstractmethod
    def get_last_by_user_id(self, user_id: str) -> Optional[SubscriptionModel]:
        raise NotImplementedError()

    @abstractmethod
    def create(
        self,
        user_id: str,
        plan_id: str,
        started_at: datetime,
        expires_at: datetime | None,
        status: str,
        is_active: bool,
        gateway: str | None,
    ) -> SubscriptionModel:
        raise NotImplementedError()

    @abstractmethod
    def cancel_active_by_user_id(
        self,
        user_id: str,
        canceled_at: datetime,
    ) -> Optional[SubscriptionModel]:
        raise NotImplementedError()
