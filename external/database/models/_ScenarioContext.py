import uuid
from typing import List
from datetime import (
    datetime, 
    timezone,
)
from sqlalchemy import (
    DateTime, 
    ForeignKey, 
    Text,
    Boolean,
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base

    
class ScenarioContext(Base):
    __tablename__ = "scenario_contexts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
    )

    key: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    ai_role_definition: Mapped[str] = mapped_column(Text, nullable=False)
    user_role_definition: Mapped[str] = mapped_column(Text, nullable=False)

    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    creator: Mapped["User"] = relationship("User", back_populates="created_scenarios")
    sessions: Mapped[List["ConversationSession"]] = relationship(
        "ConversationSession", 
        back_populates="scenario"
    )
