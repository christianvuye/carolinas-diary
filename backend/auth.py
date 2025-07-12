"""Firebase authentication module for Carolina's Diary application."""

import logging
import os
from typing import Any, Dict, Optional

import firebase_admin
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials, initialize_app

# Set up logging
logger = logging.getLogger(__name__)

# flake8: noqa: E501

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # pylint: disable=[W0212:protected-access]
    # In production, use service account key or default credentials
    # For now, we'll use default credentials (requires GOOGLE_APPLICATION_CREDENTIALS)
    try:
        cred = credentials.ApplicationDefault()
        initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    except (ValueError, FileNotFoundError, OSError) as e:
        print(f"Firebase initialization error: {e}")
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("For development, you can create a service account key file")
        # For development, you can use a service account key file
        # cred = credentials.Certificate("path/to/serviceAccountKey.json")
        # initialize_app(cred)

        # Initialize with a dummy app to prevent further errors
        try:
            # Try to initialize with project ID only for development
            PROJECT_ID = "carolina-s-journal"
            cred = credentials.ApplicationDefault()
            initialize_app(cred, {"projectId": PROJECT_ID})
            print("Firebase initialized with project ID only")
        except (ValueError, FileNotFoundError, OSError) as e2:
            print(f"Fallback initialization also failed: {e2}")
            print("Running in development mode without Firebase Auth verification")

security = HTTPBearer()


class FirebaseAuth:
    """Firebase authentication handler for managing user authentication and authorization."""

    def __init__(self) -> None:
        """Initialize the FirebaseAuth instance with security and development mode settings.
        Parameters:
            None
        Returns:
            None
        Example:
            Initializing the FirebaseAuth class will set up HTTPBearer security and determine the development mode based on the presence of GOOGLE_APPLICATION_CREDENTIALS in the environment.
        """
        self.security = HTTPBearer()
        self.development_mode = not bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

    async def get_current_user(
        self, auth_credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """
        Verify Firebase ID token and return user information
        """
        # Development mode: create a mock user when Firebase isn't properly configured
        if self.development_mode:
            print("Running in development mode - bypassing Firebase auth")
            return {
                "uid": "dev-user-123",
                "email": "developer@example.com",
                "email_verified": True,
                "name": "Developer",
                "picture": None,
                "firebase_claims": {"uid": "dev-user-123"},
            }

        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(auth_credentials.credentials)

            # Extract user information
            user_info = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "firebase_claims": decoded_token,
            }

            return user_info

        except auth.ExpiredIdTokenError as exc:
            raise HTTPException(status_code=401, detail="Token has expired") from exc
        except auth.RevokedIdTokenError as exc:
            raise HTTPException(status_code=401, detail="Token has been revoked") from exc
        except auth.InvalidIdTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc
        except ValueError as exc:
            # Log the original exception for debugging purposes
            logger.error("Authentication failed with ValueError: %s", str(exc))
            raise HTTPException(status_code=401, detail="Authentication failed") from exc

    async def get_current_user_dev_friendly(
        self, auth_credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> Dict[str, Any]:
        """
        Development-friendly version that doesn't require credentials in dev mode
        """
        # Development mode: create a mock user when Firebase isn't properly configured
        if self.development_mode:
            print("Running in development mode - bypassing Firebase auth")
            return {
                "uid": "dev-user-123",
                "email": "developer@example.com",
                "email_verified": True,
                "name": "Developer",
                "picture": None,
                "firebase_claims": {"uid": "dev-user-123"},
            }

        if not auth_credentials:
            raise HTTPException(status_code=401, detail="No credentials provided")

        return await self.get_current_user(auth_credentials)


# Global instance
firebase_auth = FirebaseAuth()


# Dependency for protected routes
async def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency function to get current authenticated user
    """
    return await firebase_auth.get_current_user(auth_credentials)


# Development-friendly dependency
async def get_current_user_dev(
    _request: Request,
    auth_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> Dict[str, Any]:
    """
    Development-friendly dependency that doesn't require auth in dev mode
    """
    if firebase_auth.development_mode:
        print("Running in development mode - bypassing Firebase auth")
        return {
            "uid": "dev-user-123",
            "email": "developer@example.com",
            "email_verified": True,
            "name": "Developer",
            "picture": None,
            "firebase_claims": {"uid": "dev-user-123"},
        }

    if not auth_credentials:
        raise HTTPException(status_code=401, detail="No credentials provided")

    return await firebase_auth.get_current_user(auth_credentials)


# Optional auth dependency (for routes that work with or without auth)
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns None if no token provided
    """
    # Development mode: return mock user
    if firebase_auth.development_mode:
        return {
            "uid": "dev-user-123",
            "email": "developer@example.com",
            "email_verified": True,
            "name": "Developer",
            "picture": None,
            "firebase_claims": {"uid": "dev-user-123"},
        }

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "firebase_claims": decoded_token,
        }
    except (
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.InvalidIdTokenError,
        ValueError,
    ):
        return None
