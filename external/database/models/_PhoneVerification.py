import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from external.database.base import Base

from ._CodeVerification import CodeVerification
# TODO - Remove this file and update all imports to use CodeVerification instead of PhoneVerification, as the latter is just an alias for the former. This was done to avoid breaking changes while refactoring the codebase to use a more generic CodeVerification model that can be used for both phone and email verification.
# Keep a compatibility alias for code that still imports PhoneVerification
PhoneVerification = CodeVerification