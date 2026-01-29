from dotenv import load_dotenv
load_dotenv()

from external.database.connection import engine
from external.database.base import Base

from external.database.models import User
from external.database.models import StudySettings
from external.database.models import Plan
from external.database.models import Subscription
from external.database.models import MessageHistory


def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
