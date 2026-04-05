from dataclasses import dataclass
from typing import Optional


@dataclass
class SubscriptionRequestDTO:
    user_id: str
    plan_id: Optional[str] = None
