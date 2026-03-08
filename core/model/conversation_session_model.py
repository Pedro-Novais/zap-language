from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from core.model.enum import ConversationSessionsState, ConversationSessionsType


class ConversationSessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    session_type: ConversationSessionsType
    status: ConversationSessionsState
    context_description: Optional[str] = None
    context_summary: Optional[str] = None
    scenario_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    