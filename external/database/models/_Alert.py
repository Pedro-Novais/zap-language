import uuid
from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column, 
)
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    UUID,
)

from external.database.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    channel: Mapped[str] = mapped_column(String(30)) 

    trigger_at: Mapped[datetime | None]
    offset_minutes: Mapped[int] = mapped_column(default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
