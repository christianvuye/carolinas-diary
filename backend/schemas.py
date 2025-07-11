"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    firebase_uid: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False
    preferences: Dict[str, Any] = {}


class UserResponse(BaseModel):
    """Schema for user response data."""

    id: int
    firebase_uid: str
    email: str
    name: Optional[str]
    picture: Optional[str]
    email_verified: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM model compatibility."""

        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user data."""

    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class JournalEntryCreate(BaseModel):
    """Schema for creating a new journal entry."""

    gratitude_answers: List[str] = []
    emotion: Optional[str] = None
    emotion_answers: List[str] = []
    custom_text: Optional[str] = None
    visual_settings: Optional[Dict[str, Any]] = None


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response data."""

    id: int
    user_id: int
    date: date
    gratitude_answers: List[str]
    emotion: Optional[str]
    emotion_answers: List[str]
    custom_text: Optional[str]
    visual_settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM model compatibility."""

        from_attributes = True


class EmotionQuestionResponse(BaseModel):
    """Schema for emotion question response data."""

    id: int
    question: str


class QuoteResponse(BaseModel):
    """Schema for quote response data."""

    quote: str
    author: str
