from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class UserCreate(BaseModel):
    firebase_uid: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False
    preferences: Dict[str, Any] = {}


class UserResponse(BaseModel):
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
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class JournalEntryCreate(BaseModel):
    gratitude_answers: List[str] = []
    emotion: Optional[str] = None
    emotion_answers: List[str] = []
    custom_text: Optional[str] = None
    visual_settings: Optional[Dict[str, Any]] = None


class JournalEntryResponse(BaseModel):
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
        from_attributes = True

    class Config:
        from_attributes = True


class EmotionQuestionResponse(BaseModel):
    id: int
    question: str


class QuoteResponse(BaseModel):
    quote: str
    author: str
