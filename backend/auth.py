from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, initialize_app, credentials
import firebase_admin
from typing import Optional
import os

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # In production, use service account key or default credentials
    # For now, we'll use default credentials (requires GOOGLE_APPLICATION_CREDENTIALS)
    try:
        cred = credentials.ApplicationDefault()
        initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        # For development, you can use a service account key file
        # cred = credentials.Certificate("path/to/serviceAccountKey.json")
        # initialize_app(cred)

security = HTTPBearer()

class FirebaseAuth:
    def __init__(self):
        self.security = HTTPBearer()
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """
        Verify Firebase ID token and return user information
        """
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
                "firebase_claims": decoded_token
            }
            
            return user_info
            
        except auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except auth.RevokedIdTokenError:
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )
        except auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {str(e)}"
            )

# Global instance
firebase_auth = FirebaseAuth()

# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency function to get current authenticated user
    """
    return await firebase_auth.get_current_user(credentials)

# Optional auth dependency (for routes that work with or without auth)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided
    """
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
            "firebase_claims": decoded_token
        }
    except Exception:
        return None