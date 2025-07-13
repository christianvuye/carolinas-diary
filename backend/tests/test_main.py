"""Tests for main FastAPI application endpoints."""

from typing import Any, Dict
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import User

# flake8: noqa: E501


class TestHealthEndpoint:
    """Test the root health endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test that the root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        expected = {"message": "Carolina's Diary API is running"}
        assert response.json() == expected


class TestUserEndpoints:
    """Test user registration and management endpoints."""

    def test_register_user_success(
        self, client: TestClient, sample_user_data: Dict[str, Any]
    ) -> None:
        """Test successful user registration."""
        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
                "name": sample_user_data["name"],
                "picture": sample_user_data["picture"],
                "email_verified": sample_user_data["email_verified"],
            }

            response = client.post("/users/register", json=sample_user_data)

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["name"] == sample_user_data["name"]
            assert "id" in data

    def test_get_current_user(
        self, client: TestClient, sample_user_data: Dict[str, Any], db_session: Session
    ) -> None:
        """Test getting current user information."""
        # First create a user in the database
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            response = client.get("/users/me")

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["name"] == sample_user_data["name"]

    def test_update_user(
        self, client: TestClient, sample_user_data: Dict[str, Any], db_session: Session
    ) -> None:
        """Test updating user information."""
        # First create a user in the database
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        update_data = {
            "name": "Updated Name",
            "preferences": {"theme": "dark", "notifications": False},
        }

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            response = client.put("/users/me", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"
            assert data["preferences"]["theme"] == "dark"


class TestJournalEndpoints:
    """Test journal entry creation and retrieval endpoints."""

    def test_create_journal_entry(
        self,
        client: TestClient,
        sample_user_data: Dict[str, Any],
        sample_journal_entry_data: Dict[str, Any],
        db_session: Session,
    ) -> None:
        """Test creating a new journal entry."""
        # First create a user
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            response = client.post("/journal-entry", json=sample_journal_entry_data)

            assert response.status_code == 200
            data = response.json()
            assert data["emotion"] == sample_journal_entry_data["emotion"]
            assert data["custom_text"] == sample_journal_entry_data["custom_text"]
            assert len(data["gratitude_answers"]) == 3

    def test_get_journal_entry_by_date(
        self,
        client: TestClient,
        sample_user_data: Dict[str, Any],
        sample_journal_entry_data: Dict[str, Any],
        db_session: Session,
    ) -> None:
        """Test retrieving a journal entry by date."""
        # Create user and journal entry first
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            # Create the entry
            client.post("/journal-entry", json=sample_journal_entry_data)

            # Retrieve the entry
            entry_date = sample_journal_entry_data["date"]
            response = client.get(f"/journal-entry/{entry_date}")

            assert response.status_code == 200
            data = response.json()
            assert data["emotion"] == sample_journal_entry_data["emotion"]

    def test_get_all_journal_entries(
        self,
        client: TestClient,
        sample_user_data: Dict[str, Any],
        sample_journal_entry_data: Dict[str, Any],
        db_session: Session,
    ) -> None:
        """Test retrieving all journal entries with pagination."""
        # Create user and journal entry first
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            # Create multiple entries
            client.post("/journal-entry", json=sample_journal_entry_data)

            # Test different entry
            entry_data_2 = sample_journal_entry_data.copy()
            entry_data_2["date"] = "2024-01-16"
            entry_data_2["emotion"] = "peaceful"
            client.post("/journal-entry", json=entry_data_2)

            # Retrieve all entries
            response = client.get("/journal-entries")

            assert response.status_code == 200
            data = response.json()
            assert "entries" in data
            assert "metadata" in data
            assert len(data["entries"]) >= 2


class TestDataEndpoints:
    """Test endpoints for getting questions, quotes, and emotions."""

    def test_get_gratitude_questions(self, client: TestClient) -> None:
        """Test getting gratitude questions."""
        response = client.get("/gratitude-questions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "question" in data[0]

    def test_get_emotion_questions(self, client: TestClient) -> None:
        """Test getting emotion-specific questions."""
        emotion = "joy"
        response = client.get(f"/emotion-questions/{emotion}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "question" in data[0]

    def test_get_quote_for_emotion(self, client: TestClient) -> None:
        """Test getting a quote for an emotion."""
        emotion = "joy"
        response = client.get(f"/quote/{emotion}")
        assert response.status_code == 200
        data = response.json()
        assert "quote" in data
        assert "author" in data
        assert "emotion" in data

    def test_get_emotions_list(self, client: TestClient) -> None:
        """Test getting the list of available emotions."""
        response = client.get("/emotions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check that standard emotions are included
        emotions = [emotion["name"] for emotion in data]
        assert "joy" in emotions
        assert "peaceful" in emotions


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_nonexistent_journal_entry(
        self, client: TestClient, sample_user_data: Dict[str, Any], db_session: Session
    ) -> None:
        """Test retrieving a non-existent journal entry."""
        # Create user first
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
            email_verified=sample_user_data["email_verified"],
        )
        db_session.add(user)
        db_session.commit()

        with patch("main.get_current_user_dev") as mock_auth:
            mock_auth.return_value = {
                "uid": sample_user_data["firebase_uid"],
                "email": sample_user_data["email"],
            }

            response = client.get("/journal-entry/2099-12-31")
            assert response.status_code == 404

    def test_invalid_emotion_questions(self, client: TestClient) -> None:
        """Test getting questions for an invalid emotion."""
        response = client.get("/emotion-questions/invalid_emotion")
        assert response.status_code == 200
        data = response.json()
        # Should return empty list for invalid emotions
        assert isinstance(data, list)
        assert len(data) == 0

    def test_invalid_emotion_quote(self, client: TestClient) -> None:
        """Test getting quote for an invalid emotion."""
        response = client.get("/quote/invalid_emotion")
        assert response.status_code == 200
        data = response.json()
        # Should return fallback quote
        assert "quote" in data
        assert "author" in data
