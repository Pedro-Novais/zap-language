
    

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Any, Dict

from pydantic import (
    BaseModel, 
    ConfigDict, 
    field_validator,
)

from core.model.enum import SystemConfigKey 


class SystemConfigModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: SystemConfigKey
    value: Dict[str, Any]
    description: Optional[str] = None
    
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    