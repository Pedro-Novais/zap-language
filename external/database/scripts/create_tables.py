from dotenv import load_dotenv
load_dotenv()

from external.database.connection import engine
from external.database.base import Base

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
