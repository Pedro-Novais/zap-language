from pydantic import BaseModel

from core.model import SubscriptionModel


class SubscriptionResponseDTO(BaseModel):
    success: bool
    message: str
    subscription: SubscriptionModel | None = None
