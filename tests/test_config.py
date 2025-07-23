import atexit
import os
import tempfile
import pytest
from sqlmodel import SQLModel, create_engine, Session
from main import app
from db import get_session

# Creates a session-wide temporary SQLite database URL
@pytest.fixture(scope="session")
def temp_db_url():
    # Create a temporary file to act as the SQLite database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite:///{path}"

    # Ensure the temp file is removed after the test session ends
    def safe_remove():
        try:
            os.remove(path)
        except PermissionError:
            pass

    atexit.register(safe_remove)
    yield url

# Creates a SQLAlchemy engine for the temporary test database
@pytest.fixture(scope="session")
def test_engine(temp_db_url):
    return create_engine(temp_db_url, echo=True)

# Initializes the schema once per test session
@pytest.fixture(scope="session", autouse=True)
def initialize_database(test_engine):
    SQLModel.metadata.create_all(test_engine)

# Overrides the application's database session dependency to use the test engine
@pytest.fixture
def session_override(test_engine):
    def get_override():
        with Session(test_engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_override
