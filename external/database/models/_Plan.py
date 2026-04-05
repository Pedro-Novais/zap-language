from __future__ import annotations

import uuid
from typing import (
    TYPE_CHECKING,
    List,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Text, ARRAY, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB

from external.database.base import Base

if TYPE_CHECKING:
    from ._Subscription import Subscription


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    price: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")
    stripe_price_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    features: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    trial_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="plan")
