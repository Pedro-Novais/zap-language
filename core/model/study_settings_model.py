from uuid import UUID
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, ConfigDict, field_validator

from core.model.enum import (
    TeacherPersonaType,
    TeacherCorrectionLevel,
    TeacherLanguageDynamics,
    UserPreferredLanguage,
)


class StudySettingsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    persona_type: TeacherPersonaType
    correction_level: TeacherCorrectionLevel
    preferred_topics: List[str]
    language_ratio: int
    language_dynamics: TeacherLanguageDynamics
    receive_newsletters: bool
    preferred_language: UserPreferredLanguage
    created_at: datetime
    
    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    