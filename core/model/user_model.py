from uuid import UUID
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    phone: Optional[str] = None
    whatsapp_enabled: bool
    created_at: datetime
    study_settings: Optional["StudySettingsModel"] = None
    messages: List["MessageHistoryModel"] = []