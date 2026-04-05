from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CreatePlanDTO:
    name: str
    slug: str
    price: int
    description: str = ""
    currency: str = "BRL"
    billing_cycle: str = "monthly"
    message_limit: int = 0
    features: Any = None
    is_active: bool = True
    trial_days: int = 0
    stripe_price_id: Optional[str] = None
