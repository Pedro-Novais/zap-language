import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DBAPIError

from contextlib import contextmanager

from core.shared.errors import ExternalServiceError


engine = create_engine(
    url=os.getenv("DATABASE_URL"),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    except DBAPIError as e:
        session.rollback()
        raise ExternalServiceError(error=e)
    finally:
        session.close()
