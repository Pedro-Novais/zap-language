from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator
from core.model.enum.verification_code_type import VerificationCodeType


class PhoneVerificationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    value: Optional[str]
    code: str
    attempts: int
    expires_at: datetime
    created_at: datetime
    code_type: VerificationCodeType
    
    @field_validator("expires_at", "created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)