import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
