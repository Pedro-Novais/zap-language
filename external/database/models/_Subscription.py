from __future__ import annotations

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
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, default=None)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    gateway: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")