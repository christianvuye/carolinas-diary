from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class JournalEntryCreate(BaseModel):
    gratitude_answers: List[str] = []
    emotion: Optional[str] = None
    emotion_answers: List[str] = []
    custom_text: Optional[str] = None
    visual_settings: Optional[Dict[str, Any]] = None

class JournalEntryResponse(BaseModel):
    id: int
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

class EmotionQuestionResponse(BaseModel):
    id: int
    question: str

class QuoteResponse(BaseModel):
    quote: str
    author: str