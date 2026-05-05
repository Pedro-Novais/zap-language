from uuid import UUID
from typing import Any

from pydantic import BaseModel, ConfigDict


class PlanModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str
    price: float
    currency: str
    billing_cycle: str
    stripe_price_id: str | None = None
    message_limit: int
    features: Any
    is_active: bool
    trial_days: int
    is_free: bool = False
