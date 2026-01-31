import uuid
from datetime import (
    datetime, 
    timezone,
)
from sqlalchemy import (
    String, 
    DateTime, 
    ForeignKey, 
    Text,
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base
from core.model import MessageRoleModel


class MessageHistory(Base):
    __tablename__ = "messages_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), default=MessageRoleModel.USER.value)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    user: Mapped["User"] = relationship("User", back_populates="messages")
    
