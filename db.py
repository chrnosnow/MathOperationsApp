from pathlib import Path

from sqlmodel import SQLModel, create_engine, Session

# Database connection URL (using SQLite)
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'requests.db'}"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Dependency function to provide a session for database operations
def get_session():
    with Session(engine) as session:
        yield session

# Create all tables defined by SQLModel models
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)