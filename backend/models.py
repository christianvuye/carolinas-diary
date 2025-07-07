from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    gratitude_answers = Column(JSON)  # List of gratitude answers
    emotion = Column(String, nullable=True)
    emotion_answers = Column(JSON)  # List of emotion-related answers
    custom_text = Column(Text, nullable=True)
    visual_settings = Column(JSON)  # Colors, fonts, stickers
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GratitudeQuestion(Base):
    __tablename__ = "gratitude_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True)

class EmotionQuestion(Base):
    __tablename__ = "emotion_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    emotion = Column(String, index=True)
    question = Column(String)

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    emotion = Column(String, index=True)
    quote = Column(Text)
    author = Column(String)