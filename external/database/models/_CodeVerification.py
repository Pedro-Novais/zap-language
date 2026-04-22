import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Enum as SAEnum, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from core.model.enum.verification_code_type import VerificationCodeType

from external.database.base import Base


class CodeVerification(Base):
    __tablename__ = 'code_verifications'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    value: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    code_type: Mapped[VerificationCodeType] = mapped_column(
        SAEnum(VerificationCodeType, name='verificationcodetype', create_type=False),
        nullable=False,
        server_default=text("'PHONE'"),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
