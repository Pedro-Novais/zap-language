import uuid
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    whatsapp_enabled: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    study_settings: Mapped["StudySettings"] = relationship(
        "StudySettings", 
        back_populates="user", 
        uselist=False,
    )
    messages: Mapped[List["MessageHistory"]] = relationship(
        "MessageHistory", 
        back_populates="user", 
        cascade="all, delete-orphan",
    )
