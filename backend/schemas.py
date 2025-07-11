"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel


class Emotion(str, Enum):
    """Valid emotions for journaling prompts and quotes."""

    ANXIETY = "anxiety"
    SADNESS = "sadness"
    STRESS = "stress"
    EXCITEMENT = "excitement"
    ANGER = "anger"
    HAPPINESS = "happiness"
    JOY = "joy"
    FEELING_OVERWHELMED = "feeling overwhelmed"
    JEALOUSY = "jealousy"
    FATIGUE = "fatigue"
    INSECURITY = "insecurity"
    DOUBT = "doubt"
    CATASTROPHIC_THINKING = "catastrophic thinking"


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
    emotion: Optional[Emotion] = None
    emotion_answers: List[str] = []
    custom_text: Optional[str] = None
    visual_settings: Optional[Dict[str, Any]] = None


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response data."""

    id: int
    user_id: int
    date: date
    gratitude_answers: List[str]
    emotion: Optional[Emotion]
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


class PaginationMetadata(BaseModel):
    """Schema for pagination metadata."""

    current_page: int
    page_size: int
    total_pages: int
    total_items: int
    has_next: bool
    has_previous: bool


class PaginatedJournalEntriesResponse(BaseModel):
    """Schema for paginated journal entries response."""

    entries: List[JournalEntryResponse]
    pagination: PaginationMetadata

    class Config:
        """Pydantic configuration for ORM model compatibility."""

        from_attributes = True
