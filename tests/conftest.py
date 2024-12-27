import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.helpers.database import db
from app.models.base import Base
from app.models.user import User

load_dotenv(dotenv_path=".env")

get_db = db()


def construct_database_url():
    """
    Constructs a database URL based on environment variables.

    The function supports SQLite, PostgreSQL, and MySQL databases. It reads the
    following environment variables to construct the URL:

    - DB_TYPE: The type of the database (default is "sqlite").
    - DB_HOST: The database host (default is "localhost").
    - DB_PORT: The database port (default is "5432").
    - DB_USERNAME: The database username (default is "user").
    - DB_PASSWORD: The database password (default is "password").

    Returns:
        str: The constructed database URL.

    Raises:
        ValueError: If the specified database type is unsupported.
    """
    db_type = os.environ.get("DB_TYPE", "sqlite")
    db_name = "spartan.db"
    if db_type == "sqlite":
        return f"sqlite:///./database/{db_name}"
    else:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_username = os.getenv("DB_USERNAME", "user")
        db_password = os.getenv("DB_PASSWORD", "password")

        if db_type == "psql":
            return f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

        elif db_type == "mysql":
            return f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


@pytest.fixture(scope="module")
def test_db_session():
    """
    Fixture to set up and tear down a test database session.

    This fixture creates an engine and a session for a test database,
    yielding the session to be used in tests. After the tests are done,
    it closes the session and drops all tables in the test database.

    Yields:
        db (Session): SQLAlchemy session object for the test database.
    """
    TEST_DATABASE_URL = construct_database_url()

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_data(test_db_session):
    """
    Fixture to create and yield test user data.

    This fixture creates five test users, adds them to the test database session,
    and commits the session. After yielding the users, it cleans up by deleting
    the users from the test database session and committing the session again.

    Args:
        test_db_session: The database session used for testing.

    Yields:
        list: A list of created User objects.
    """
    users = [
        User(
            username=f"testuser{i}",
            email=f"testuser{i}@example.com",
            password="password123",
        )
        for i in range(1, 6)
    ]

    for user in users:
        test_db_session.add(user)
    test_db_session.commit()

    yield users

    for user in users:
        test_db_session.delete(user)
    test_db_session.commit()
