"""Database configuration and setup for Carolina's Diary application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./carolinas_diary.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)  # flake8: noqa: E501
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models using typed declarative style."""
