from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, initialize_app, credentials
import firebase_admin
from typing import Optional
import os
import threading
import time
import uuid

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # In production, use service account key or default credentials
    # For now, we'll use default credentials (requires GOOGLE_APPLICATION_CREDENTIALS)
    try:
        cred = credentials.ApplicationDefault()
        initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("For development, you can create a service account key file")
        # For development, you can use a service account key file
        # cred = credentials.Certificate("path/to/serviceAccountKey.json")
        # initialize_app(cred)
        
        # Initialize with a dummy app to prevent further errors
        try:
            # Try to initialize with project ID only for development
            project_id = "carolina-s-journal"
            cred = credentials.ApplicationDefault()
            initialize_app(cred, {'projectId': project_id})
            print("Firebase initialized with project ID only")
        except Exception as e2:
            print(f"Fallback initialization also failed: {e2}")
            print("Running in development mode without Firebase Auth verification")

security = HTTPBearer()


class FirebaseAuth:
    def __init__(self):
        self.security = HTTPBearer()
        self.development_mode = not bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        self._dev_sessions = {}  # Store development user sessions
        self._session_lock = threading.Lock()  # Thread-safe session management

    def _get_or_create_dev_session(self, session_id: str) -> dict:
        """Get or create a consistent development session"""
        with self._session_lock:
            if session_id not in self._dev_sessions:
                # Create a new consistent session
                self._dev_sessions[session_id] = {
                    "uid": f"dev-user-{uuid.uuid4().hex[:8]}",
                    "email": "developer@example.com",
                    "email_verified": True,
                    "name": "Developer",
                    "picture": None,
                    "firebase_claims": {"uid": f"dev-user-{uuid.uuid4().hex[:8]}"},
                    "created_at": time.time()
                }
            return self._dev_sessions[session_id]

    def _cleanup_old_sessions(self):
        """Clean up sessions older than 24 hours"""
        current_time = time.time()
        with self._session_lock:
            expired_sessions = [
                session_id for session_id, session_data in self._dev_sessions.items()
                if current_time - session_data.get("created_at", 0) > 86400  # 24 hours
            ]
            for session_id in expired_sessions:
                del self._dev_sessions[session_id]

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
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
            decoded_token = auth.verify_id_token(credentials.credentials)

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

        except auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except auth.RevokedIdTokenError:
            raise HTTPException(status_code=401, detail="Token has been revoked")
        except auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Authentication failed: {str(e)}"
            )
    
    async def get_current_user_dev_friendly(
        self, credentials: HTTPAuthorizationCredentials = None
    ) -> dict:
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
        
        if not credentials:
            raise HTTPException(status_code=401, detail="No credentials provided")
            
        return await self.get_current_user(credentials)


# Global instance
firebase_auth = FirebaseAuth()


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency function to get current authenticated user
    """
    return await firebase_auth.get_current_user(credentials)


# Development-friendly dependency with session management
async def get_current_user_dev(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> dict:
    """
    Development-friendly dependency that doesn't require auth in dev mode
    """
    if firebase_auth.development_mode:
        # Clean up old sessions periodically
        firebase_auth._cleanup_old_sessions()
        
        # Get session ID from request headers or create new one
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create consistent session
        session_data = firebase_auth._get_or_create_dev_session(session_id)
        
        print(f"Running in development mode - using session: {session_id}")
        return session_data
    
    if not credentials:
        raise HTTPException(status_code=401, detail="No credentials provided")
        
    return await firebase_auth.get_current_user(credentials)


# Optional auth dependency (for routes that work with or without auth)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided
    """
    # Development mode: return mock user with session management
    if firebase_auth.development_mode:
        firebase_auth._cleanup_old_sessions()
        
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session_data = firebase_auth._get_or_create_dev_session(session_id)
        return session_data
    
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
    except Exception:
        return None
