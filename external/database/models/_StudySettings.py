import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy import (
    String, 
    DateTime, 
    UUID,
    ForeignKey,
)

from external.database.base import Base


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
    )
    receive_newsletters: Mapped[bool] = mapped_column(default=True)
    preferred_language: Mapped[str] = mapped_column(String(50), default="en")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    user: Mapped["User"] = relationship("User", back_populates="study_settings")