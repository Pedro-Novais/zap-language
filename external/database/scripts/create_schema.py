from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from external.database.connection import engine

def create_schema():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS routine"))
        conn.commit()

if __name__ == "__main__":
    create_schema()
