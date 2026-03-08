import uuid
from datetime import (
    datetime, 
)
from typing import List
from sqlalchemy import (
    DateTime, 
    ForeignKey, 
    Text,
    Boolean,
    Enum
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base
from core.model.enum import (
    ConversationSessionsState,
    ConversationSessionsType,
)


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    session_type: Mapped[ConversationSessionsType] = mapped_column(
        Enum(ConversationSessionsType), 
        default=ConversationSessionsType.FREE_TALK,
        nullable=False
    )
    
    status: Mapped[ConversationSessionsState] = mapped_column(
        Enum(ConversationSessionsState), 
        default=ConversationSessionsState.UNDEFINED,
    )

    context_description: Mapped[str] = mapped_column(Text, nullable=True)
    context_summary: Mapped[str] = mapped_column(Text, nullable=True)

    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenario_contexts.id", ondelete="SET NULL"), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["MessageHistory"]] = relationship("MessageHistory", back_populates="session", cascade="all, delete-orphan")
    scenario: Mapped["ScenarioContext"] = relationship("ScenarioContext", back_populates="sessions")
