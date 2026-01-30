from uuid import UUID
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator


class PhoneVerificationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    phone_number: str
    code: str
    attempts: int
    expires_at: datetime
    created_at: datetime
    
    @field_validator("expires_at", "created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)