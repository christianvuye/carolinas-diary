from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    JSON,
    ForeignKey,
    Boolean,
    Float,
    Time,
)
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
    user_sessions = relationship("UserSession", back_populates="user")
    feature_usage = relationship("FeatureUsage", back_populates="user")


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

    # Analytics fields
    entry_length = Column(Integer, default=0)  # Character count
    completion_time = Column(Float, nullable=True)  # Time in seconds to complete
    is_completed = Column(Boolean, default=False)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="journal_entries")
    session = relationship("UserSession", back_populates="journal_entries")


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


# Analytics Models

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_start = Column(DateTime, default=func.now())
    session_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)  # mobile, desktop, tablet

    # Relationships
    user = relationship("User", back_populates="user_sessions")
    journal_entries = relationship("JournalEntry", back_populates="session")
    feature_usage = relationship("FeatureUsage", back_populates="session")


class FeatureUsage(Base):
    __tablename__ = "feature_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)
    feature_name = Column(String, index=True)  # journal_prompt, emotion_tracking, etc.
    feature_data = Column(JSON, nullable=True)  # Additional data about the feature usage
    usage_time = Column(DateTime, default=func.now())
    duration_seconds = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="feature_usage")
    session = relationship("UserSession", back_populates="feature_usage")


class UserRetention(Base):
    __tablename__ = "user_retention"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cohort_date = Column(Date, index=True)  # When user first signed up
    retention_date = Column(Date, index=True)  # Date to check retention
    is_retained = Column(Boolean, default=False)  # Whether user was active on retention_date
    days_since_signup = Column(Integer, index=True)  # Days since cohort_date
    activity_count = Column(Integer, default=0)  # Number of activities on retention_date

    # Relationships
    user = relationship("User")


class DailyActiveUsers(Base):
    __tablename__ = "daily_active_users"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)


class WeeklyActiveUsers(Base):
    __tablename__ = "weekly_active_users"

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, unique=True, index=True)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)


class MonthlyActiveUsers(Base):
    __tablename__ = "monthly_active_users"

    id = Column(Integer, primary_key=True, index=True)
    month_start = Column(Date, unique=True, index=True)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)


class EntryCompletionMetrics(Base):
    __tablename__ = "entry_completion_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    total_entries_started = Column(Integer, default=0)
    total_entries_completed = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    avg_completion_time = Column(Float, default=0.0)
    avg_entry_length = Column(Float, default=0.0)
