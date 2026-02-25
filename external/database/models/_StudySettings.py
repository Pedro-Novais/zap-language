import uuid
from datetime import (
    datetime, 
    timezone,
)
from typing import List

from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy import (
    DateTime, 
    UUID,
    ForeignKey,
    Integer,
    Enum,
    Boolean,
    ARRAY,
    String
)

from external.database.base import Base
from core.model.enum import (
    TeacherPersonaType, 
    TeacherCorrectionLevel, 
    TeacherLanguageDynamics,
    UserPreferredLanguage,
)


class StudySettings(Base):
    __tablename__ = "study_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"),
        unique=True,
    )
    persona_type: Mapped[TeacherPersonaType] = mapped_column(Enum(TeacherPersonaType), default=TeacherPersonaType.FRIENDLY)
    correction_level: Mapped[TeacherCorrectionLevel] = mapped_column(Enum(TeacherCorrectionLevel), default=TeacherCorrectionLevel.LIGHT)
    preferred_topics: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    language_ratio: Mapped[int] = mapped_column(Integer, default=100)
    language_dynamics: Mapped[TeacherLanguageDynamics] = mapped_column(Enum(TeacherLanguageDynamics), default=TeacherLanguageDynamics.BILINGUE)
    receive_newsletters: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_language: Mapped[UserPreferredLanguage] = mapped_column(Enum(UserPreferredLanguage), default=UserPreferredLanguage.ENGLISH)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    user: Mapped["User"] = relationship("User", back_populates="study_settings")
