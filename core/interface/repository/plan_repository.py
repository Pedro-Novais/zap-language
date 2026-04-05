from abc import ABC, abstractmethod
from typing import Any, List, Optional

from core.model import PlanModel


class PlanRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[PlanModel]:
        raise NotImplementedError()

    @abstractmethod
    def create(
        self,
        name: str,
        slug: str,
        price: int,
        description: str,
        currency: str,
        billing_cycle: str,
        message_limit: int,
        features: Any,
        is_active: bool,
        trial_days: int,
        stripe_price_id: Optional[str],
    ) -> PlanModel:
        raise NotImplementedError()
