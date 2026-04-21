from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, Field

from core.model import StudySettingsModel


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    phone: Optional[str] = None
    whatsapp_enabled: bool
    is_admin: bool = False
    created_at: datetime
    google_id: Optional[str] = Field(default=None, exclude=True)
    last_login: Optional[datetime] = Field(default=None, exclude=True)
    study_settings: Optional[StudySettingsModel] = None
    password: str = Field(exclude=True)
    current_topic: str | None = None
    
    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @field_validator("last_login", mode="after")
    @classmethod
    def ensure_last_login_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
