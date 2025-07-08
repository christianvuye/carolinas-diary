from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    
    # User preferences
    preferences = Column(JSON, default={})  # Theme, notification settings, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, index=True)
    gratitude_answers = Column(JSON)  # List of gratitude answers
    emotion = Column(String, nullable=True)
    emotion_answers = Column(JSON)  # List of emotion-related answers
    custom_text = Column(Text, nullable=True)
    visual_settings = Column(JSON)  # Colors, fonts, stickers
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")

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