from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from core.model import PlanModel


class SubscriptionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    plan_id: UUID
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    gateway: Optional[str] = None
    plan: Optional[PlanModel] = None

    @field_validator("started_at", mode="after")
    @classmethod
    def ensure_started_at_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("expires_at", mode="after")
    @classmethod
    def ensure_expires_at_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
