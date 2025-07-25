import atexit
import os
import tempfile

import pytest
import pytest_asyncio
from sqlalchemy.future import select
from sqlmodel import Session, SQLModel, create_engine

from core.security import hash_password
from db import get_session
from main import app
from models.users import Role, User


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


# Overrides the application's database
# session dependency to use the test engine
@pytest.fixture
def session_override(test_engine):
    def get_override():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_override


@pytest.fixture
def seed_admin(test_engine):
    # Add admin role and admin user
    with Session(test_engine) as session:
        # Ensure admin role exists
        role = session.exec(select(Role).where(Role.name == "admin")).first()
        if not role:
            role = Role(name="admin")
            session.add(role)
            session.commit()
            session.refresh(role)
        # Ensure admin user exists
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            user = User(
                username="admin",
                hashed_password=hash_password("adminpass"),
                is_active=True,
            )
            user.roles.append(role)
            session.add(user)
            session.commit()
            session.refresh(user)
    yield


@pytest_asyncio.fixture
async def admin_token(client, seed_admin):
    # OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    data = {"username": "admin", "password": "adminpass"}
    response = await client.post("/auth/login", data=data)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def token_user(client, session_override):
    data = {"username": "basicuser", "password": "userpass"}

    # Register the user if not already present
    await client.post(
        "/auth/register", json={"username": "basicuser", "password": "userpass"}
    )

    # Login
    response = await client.post("/auth/login", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]
