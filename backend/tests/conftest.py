"""Shared pytest fixtures for backend testing."""

import os
import tempfile
from typing import Any, Dict, Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database import Base
from main import app, get_db

# flake8: noqa: E501


@pytest.fixture(scope="function")
def temp_db() -> Generator[Any, None, None]:
    """Create a temporary SQLite database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Create test database engine
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    engine.dispose()
    os.unlink(db_path)


@pytest.fixture
def db_session(temp_db: Any) -> Generator[Session, None, None]:  # noqa: F811
    """Create a database session for testing."""
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=temp_db
    )
    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_firebase_user() -> Dict[str, Any]:
    """Mock Firebase user data for testing."""
    return {
        "uid": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/picture.jpg",
        "email_verified": True,
    }


@pytest.fixture
def mock_auth_dev_mode() -> Generator[Any, None, None]:
    """Mock authentication in development mode."""
    with patch("main.get_current_user_dev") as mock_get_user_dev:
        mock_get_user_dev.return_value = {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "email_verified": True,
        }
        yield mock_get_user_dev


@pytest.fixture
def mock_firebase_auth(
    mock_firebase_user: Dict[str, Any],
) -> Generator[Any, None, None]:
    """Mock Firebase authentication for testing."""
    with patch("auth.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = mock_firebase_user
        yield mock_verify


@pytest.fixture
def client(
    db_session: Session, mock_auth_dev_mode: Any
) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(
    client: TestClient, mock_firebase_user: Dict[str, Any]
) -> Generator[TestClient, None, None]:
    """Create an authenticated test client."""
    # Already authenticated via mock_auth_dev_mode
    yield client


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "firebase_uid": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/picture.jpg",
        "email_verified": True,
        "preferences": {"theme": "light", "notifications": True},
    }


@pytest.fixture
def sample_journal_entry_data() -> Dict[str, Any]:
    """Sample journal entry data for testing."""
    return {
        "date": "2024-01-15",
        "gratitude_answers": [
            "I'm grateful for my family",
            "I'm grateful for good health",
            "I'm grateful for this opportunity",
        ],
        "emotion": "joy",
        "emotion_answers": [
            "I feel joyful because of my achievements",
            "The sunny weather makes me happy",
        ],
        "custom_text": "Today was a wonderful day filled with positive experiences.",
        "visual_settings": {"theme": "sunny", "color": "#FFD700"},
    }
