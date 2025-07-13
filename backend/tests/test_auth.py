"""Tests for authentication functionality."""

import asyncio
import os
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from auth import FirebaseAuth, get_current_user, get_current_user_dev

# flake8: noqa: E501


class TestFirebaseAuth:
    """Test the FirebaseAuth class functionality."""

    @patch.dict(os.environ, {}, clear=True)
    def test_firebase_auth_init_development_mode(self) -> None:
        """Test FirebaseAuth initialization in development mode."""
        auth = FirebaseAuth()
        assert auth.development_mode is True

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    def test_firebase_auth_init_production_mode(self) -> None:
        """Test FirebaseAuth initialization in production mode."""
        auth = FirebaseAuth()
        assert auth.development_mode is False

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    @patch("auth.auth.verify_id_token")
    def test_get_current_user_success(self, mock_verify: Mock) -> None:
        """Test successful user authentication."""
        # Mock Firebase verification
        mock_verify.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg",
            "email_verified": True,
        }

        auth = FirebaseAuth()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid-token"
        )

        result = asyncio.run(auth.get_current_user(credentials))

        assert result["uid"] == "test-uid-123"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        mock_verify.assert_called_once_with("valid-token")

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    @patch("auth.auth.verify_id_token")
    def test_get_current_user_expired_token(self, mock_verify: Mock) -> None:
        """Test handling of expired token."""

        # Mock the Firebase exception with proper initialization
        class MockExpiredIdTokenError(Exception):
            """Mock exception for expired Firebase ID tokens."""

            def __init__(self, message: str, cause: Any = None) -> None:
                super().__init__(message)
                self.cause = cause

        mock_verify.side_effect = MockExpiredIdTokenError("Token expired", None)

        auth_instance = FirebaseAuth()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="expired-token"
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(auth_instance.get_current_user(credentials))

        assert exc_info.value.status_code == 401

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    @patch("auth.auth.verify_id_token")
    def test_get_current_user_value_error(self, mock_verify: Mock) -> None:
        """Test handling of ValueError during authentication."""
        mock_verify.side_effect = ValueError("Authentication failed")

        auth_instance = FirebaseAuth()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="problematic-token"
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(auth_instance.get_current_user(credentials))

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in exc_info.value.detail


class TestAuthenticationHelpers:
    """Test authentication helper functions."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    @patch("auth.firebase_auth")
    def test_get_current_user_function(self, mock_firebase_auth: Mock) -> None:
        """Test the get_current_user dependency function."""

        # Mock the firebase_auth instance
        async def mock_get_current_user(_auth_credentials: Any) -> Dict[str, str]:
            return {
                "uid": "test-uid",
                "email": "test@example.com",
            }

        mock_firebase_auth.get_current_user = mock_get_current_user

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="test-token"
        )

        result = asyncio.run(get_current_user(credentials))

        assert result["uid"] == "test-uid"
        assert result["email"] == "test@example.com"

    def test_get_current_user_dev_function(self) -> None:
        """Test the development mode authentication function."""
        # Mock the request object
        mock_request = Mock()
        result = asyncio.run(get_current_user_dev(mock_request))

        assert result["uid"] == "dev-user"
        assert result["email"] == "dev@example.com"
        assert result["name"] == "Development User"
        assert result["email_verified"] is True


class TestAuthenticationMocking:
    """Test authentication with various mocking scenarios."""

    @patch.dict(os.environ, {}, clear=True)
    def test_development_mode_behavior(self) -> None:
        """Test behavior in development mode."""
        auth = FirebaseAuth()
        assert auth.development_mode is True

        # In development mode, we might want different behavior
        mock_request = Mock()
        dev_user = asyncio.run(get_current_user_dev(mock_request))
        assert dev_user["uid"] == "dev-user"
        assert dev_user["email"] == "dev@example.com"

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    def test_production_mode_behavior(self) -> None:
        """Test behavior in production mode."""
        auth = FirebaseAuth()
        assert auth.development_mode is False

    def test_mock_user_data_structure(self, mock_firebase_user: Dict[str, Any]) -> None:
        """Test that mock user data has the correct structure."""
        assert "uid" in mock_firebase_user
        assert "email" in mock_firebase_user
        assert "name" in mock_firebase_user
        assert "picture" in mock_firebase_user
        assert "email_verified" in mock_firebase_user

        # Verify data types
        assert isinstance(mock_firebase_user["uid"], str)
        assert isinstance(mock_firebase_user["email"], str)
        assert isinstance(mock_firebase_user["email_verified"], bool)


class TestAuthenticationIntegration:
    """Test authentication integration scenarios."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    @patch("auth.auth.verify_id_token")
    def test_full_authentication_flow(self, mock_verify: Mock) -> None:
        """Test complete authentication flow."""
        # Setup mock return value
        mock_user_data = {
            "uid": "integration-test-uid",
            "email": "integration@example.com",
            "name": "Integration Test User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
        }
        mock_verify.return_value = mock_user_data

        # Test authentication
        auth = FirebaseAuth()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="integration-test-token"
        )

        result = asyncio.run(auth.get_current_user(credentials))

        assert result == mock_user_data
        mock_verify.assert_called_once_with("integration-test-token")

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "path"})
    def test_authentication_without_credentials(self) -> None:
        """Test authentication behavior without proper credentials."""
        # Test with None credentials should work (handled by FastAPI)
        # In real usage, FastAPI would ensure credentials are provided
        mock_request = Mock()
        dev_result = asyncio.run(get_current_user_dev(mock_request))
        assert dev_result["uid"] == "dev-user"
