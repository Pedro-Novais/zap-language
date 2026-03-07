import uuid
from datetime import (
    datetime, 
    timezone,
)
from typing import List
from sqlalchemy import (
    DateTime, 
    ForeignKey, 
    Text,
    Boolean,
    text,
    Enum
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base
from core.model.enum import ConversationSessionsState


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    status: Mapped[ConversationSessionsState] = mapped_column(Enum(ConversationSessionsState), default=ConversationSessionsState.AWAITING_DEFINITION)
    
    scenario_key: Mapped[str] = mapped_column(Text, nullable=True)
    
    context_summary: Mapped[str] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        index=True,
        server_default=text('true')
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["MessageHistory"]] = relationship(
        "MessageHistory", 
        back_populates="session", 
        cascade="all, delete-orphan"
    )
    scenario: Mapped["ScenarioContext"] = relationship("ScenarioContext", back_populates="sessions")
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scenario_contexts.id", ondelete="SET NULL"), 
        nullable=True,
    )
