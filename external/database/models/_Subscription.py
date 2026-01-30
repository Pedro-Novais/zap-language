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
    Integer, 
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    gateway: Mapped[str | None] = mapped_column(String)