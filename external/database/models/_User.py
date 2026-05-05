from __future__ import annotations

import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship,
)
from sqlalchemy import String, DateTime, event, select
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base

if TYPE_CHECKING:
    from ._ConversationSession import ConversationSession
    from ._MessageHistory import MessageHistory
    from ._ScenarioContext import ScenarioContext
    from ._StudySettings import StudySettings
    from ._Subscription import Subscription


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
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    sub: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    whatsapp_enabled: Mapped[bool] = mapped_column(default=False)
    is_valid: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    payment_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True)
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
    sessions: Mapped[list["ConversationSession"]] = relationship(
        "ConversationSession", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_scenarios: Mapped[List["ScenarioContext"]] = relationship("ScenarioContext", back_populates="creator")
    
def set_default_subscription(
    mapper, 
    connection, 
    target,
) -> None:

    from ._Subscription import Subscription
    from ._Plan import Plan
    
    plan_query = select(Plan.id).where(Plan.is_free == True).limit(1)
    plan_id = connection.execute(plan_query).scalar()
    if plan_id:
        connection.execute(
            Subscription.__table__.insert().values(
                id=uuid.uuid4(),
                user_id=target.id,
                plan_id=plan_id,
                expires_at=None,
            )
        )

event.listen(User, "after_insert", set_default_subscription)
