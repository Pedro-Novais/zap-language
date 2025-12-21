from dotenv import load_dotenv
load_dotenv()

from external.database.connection import engine
from external.database.base import Base

from external.database.models._User import User
from external.database.models._Alert import Alert
from external.database.models._UserSettings import UserSettings

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
