from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class ScenarioModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creator_id: Optional[UUID] = None
    key: str
    name: str
    description: str
    ai_role_definition: str
    user_role_definition: str
    is_public: bool
    created_at: datetime

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    