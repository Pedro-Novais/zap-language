from uuid import UUID
from datetime import (
    datetime, 
    timezone,
)
from typing import Optional

from pydantic import (
    BaseModel, 
    ConfigDict, 
    field_validator,
)

from core.model.enum import MessageRoleModel


class MessageHistoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: MessageRoleModel
    content: str
    is_allowed: bool = True
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    
    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    