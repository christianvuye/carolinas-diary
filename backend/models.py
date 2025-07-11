"""SQLAlchemy models for the journal application."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

# flake8: noqa: E501


class User(Base):
    """User model for authentication and preferences."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    firebase_uid: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # User preferences
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="user"
    )


class JournalEntry(Base):
    """Journal entry model containing gratitude, emotions, and custom text."""

    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(Date, index=True)
    gratitude_answers: Mapped[List[str]] = mapped_column(JSON)
    emotion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emotion_answers: Mapped[List[str]] = mapped_column(JSON)
    custom_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visual_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="journal_entries")


class GratitudeQuestion(Base):
    """Gratitude question model for prompting user responses."""

    __tablename__ = "gratitude_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(String, unique=True)


class EmotionQuestion(Base):
    """Emotion-specific question model for guided journaling."""

    __tablename__ = "emotion_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emotion: Mapped[str] = mapped_column(String, index=True)
    question: Mapped[str] = mapped_column(String)


class Quote(Base):
    """Inspirational quote model organized by emotion."""

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emotion: Mapped[str] = mapped_column(String, index=True)
    quote: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String)
