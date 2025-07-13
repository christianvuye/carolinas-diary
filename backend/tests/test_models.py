"""Tests for SQLAlchemy database models."""

from datetime import date
from typing import Any, Dict

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import EmotionQuestion, GratitudeQuestion, JournalEntry, Quote, User


# flake8: noqa: E501
class TestUserModel:
    """Test the User model functionality."""

    def test_create_user(self, db_session: Session) -> None:
        """Test creating a new user."""
        user = User(
            firebase_uid="test-uid-123",
            email="test@example.com",
            name="Test User",
            email_verified=True,
            preferences={"theme": "light"},
        )

        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.firebase_uid == "test-uid-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.email_verified is True
        assert user.preferences["theme"] == "light"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_unique_constraints(self, db_session: Session) -> None:
        """Test that user constraints are enforced."""
        # Create first user
        user1 = User(
            firebase_uid="test-uid-123", email="test@example.com", name="Test User 1"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create user with same firebase_uid
        user2 = User(
            firebase_uid="test-uid-123",
            email="different@example.com",
            name="Test User 2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_relationships(self, db_session: Session) -> None:
        """Test user relationships with journal entries."""
        user = User(
            firebase_uid="test-uid-123", email="test@example.com", name="Test User"
        )
        db_session.add(user)
        db_session.commit()

        # Create journal entry
        entry = JournalEntry(
            user_id=user.id,
            date=date(2024, 1, 15),
            gratitude_answers=["grateful for family"],
            emotion="joy",
            emotion_answers=["feeling joyful"],
        )
        db_session.add(entry)
        db_session.commit()

        # Test relationship
        assert len(user.journal_entries) == 1
        assert user.journal_entries[0].emotion == "joy"


class TestJournalEntryModel:
    """Test the JournalEntry model functionality."""

    def test_create_journal_entry(
        self, db_session: Session, sample_user_data: Dict[str, Any]
    ) -> None:
        """Test creating a new journal entry."""
        # Create user first
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
        )
        db_session.add(user)
        db_session.commit()

        # Create journal entry
        entry = JournalEntry(
            user_id=user.id,
            date=date(2024, 1, 15),
            gratitude_answers=[
                "grateful for family",
                "grateful for health",
                "grateful for opportunities",
            ],
            emotion="joy",
            emotion_answers=["feeling happy", "celebrating success"],
            custom_text="Today was amazing!",
            visual_settings={"theme": "sunny", "color": "#FFD700"},
        )

        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert entry.user_id == user.id
        assert entry.date == date(2024, 1, 15)
        assert len(entry.gratitude_answers) == 3
        assert entry.emotion == "joy"
        assert entry.custom_text == "Today was amazing!"
        assert entry.visual_settings is not None
        assert entry.visual_settings["theme"] == "sunny"
        assert entry.created_at is not None

    def test_journal_entry_user_relationship(
        self, db_session: Session, sample_user_data: Dict[str, Any]
    ) -> None:
        """Test journal entry relationship with user."""
        # Create user
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
        )
        db_session.add(user)
        db_session.commit()

        # Create journal entry
        entry = JournalEntry(
            user_id=user.id,
            date=date(2024, 1, 15),
            gratitude_answers=["grateful for today"],
            emotion="peaceful",
            emotion_answers=["feeling calm"],
        )
        db_session.add(entry)
        db_session.commit()

        # Test relationship
        assert entry.user.email == sample_user_data["email"]
        assert entry.user.name == sample_user_data["name"]

    def test_journal_entry_optional_fields(
        self, db_session: Session, sample_user_data: Dict[str, Any]
    ) -> None:
        """Test journal entry with optional fields."""
        # Create user
        user = User(
            firebase_uid=sample_user_data["firebase_uid"],
            email=sample_user_data["email"],
            name=sample_user_data["name"],
        )
        db_session.add(user)
        db_session.commit()

        # Create minimal journal entry
        entry = JournalEntry(
            user_id=user.id,
            date=date(2024, 1, 15),
            gratitude_answers=["grateful for life"],
            emotion_answers=[],
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.emotion is None
        assert entry.custom_text is None
        assert entry.visual_settings is None


class TestGratitudeQuestionModel:
    """Test the GratitudeQuestion model functionality."""

    def test_create_gratitude_question(self, db_session: Session) -> None:
        """Test creating a gratitude question."""
        question = GratitudeQuestion(question="What made you smile today?")

        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.question == "What made you smile today?"

    def test_gratitude_question_unique_constraint(self, db_session: Session) -> None:
        """Test that gratitude questions must be unique."""
        question1 = GratitudeQuestion(question="What made you smile today?")
        db_session.add(question1)
        db_session.commit()

        # Try to create duplicate
        question2 = GratitudeQuestion(question="What made you smile today?")
        db_session.add(question2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestEmotionQuestionModel:
    """Test the EmotionQuestion model functionality."""

    def test_create_emotion_question(self, db_session: Session) -> None:
        """Test creating an emotion question."""
        question = EmotionQuestion(
            emotion="joy", question="What brought you joy today?"
        )

        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.emotion == "joy"
        assert question.question == "What brought you joy today?"

    def test_multiple_questions_same_emotion(self, db_session: Session) -> None:
        """Test multiple questions for the same emotion."""
        question1 = EmotionQuestion(
            emotion="joy", question="What brought you joy today?"
        )
        question2 = EmotionQuestion(
            emotion="joy", question="How did you express your joy?"
        )

        db_session.add(question1)
        db_session.add(question2)
        db_session.commit()

        # Query questions for joy emotion
        joy_questions = (
            db_session.query(EmotionQuestion)
            .filter(EmotionQuestion.emotion == "joy")
            .all()
        )

        assert len(joy_questions) == 2
        assert "brought you joy" in joy_questions[0].question
        assert "express your joy" in joy_questions[1].question


class TestQuoteModel:
    """Test the Quote model functionality."""

    def test_create_quote(self, db_session: Session) -> None:
        """Test creating a quote."""
        quote = Quote(
            emotion="inspiration",
            quote="The only way to do great work is to love what you do.",
            author="Steve Jobs",
        )

        db_session.add(quote)
        db_session.commit()

        assert quote.id is not None
        assert quote.emotion == "inspiration"
        assert "great work" in quote.quote
        assert quote.author == "Steve Jobs"

    def test_multiple_quotes_same_emotion(self, db_session: Session) -> None:
        """Test multiple quotes for the same emotion."""
        quote1 = Quote(
            emotion="motivation",
            quote="Success is not final, failure is not fatal.",
            author="Winston Churchill",
        )
        quote2 = Quote(
            emotion="motivation",
            quote="The future belongs to those who believe.",
            author="Eleanor Roosevelt",
        )

        db_session.add(quote1)
        db_session.add(quote2)
        db_session.commit()

        # Query quotes for motivation emotion
        motivation_quotes = (
            db_session.query(Quote).filter(Quote.emotion == "motivation").all()
        )

        assert len(motivation_quotes) == 2
        authors = [q.author for q in motivation_quotes]
        assert "Winston Churchill" in authors
        assert "Eleanor Roosevelt" in authors


class TestModelIntegration:
    """Test integration between different models."""

    def test_complete_user_journey(self, db_session: Session) -> None:
        """Test a complete user journey with all models."""
        # Create user
        user = User(
            firebase_uid="journey-user",
            email="journey@example.com",
            name="Journey User",
        )
        db_session.add(user)
        db_session.commit()

        # Create gratitude questions
        gratitude_q = GratitudeQuestion(question="What are you grateful for?")
        db_session.add(gratitude_q)

        # Create emotion questions
        emotion_q = EmotionQuestion(
            emotion="gratitude", question="How did gratitude affect your day?"
        )
        db_session.add(emotion_q)

        # Create quote
        quote = Quote(
            emotion="gratitude",
            quote="Gratitude turns what we have into enough.",
            author="Anonymous",
        )
        db_session.add(quote)
        db_session.commit()

        # Create journal entry using the data
        entry = JournalEntry(
            user_id=user.id,
            date=date.today(),
            gratitude_answers=["Family", "Health", "Opportunities"],
            emotion="gratitude",
            emotion_answers=["Made me appreciate life more"],
        )
        db_session.add(entry)
        db_session.commit()

        # Verify everything is connected
        assert len(user.journal_entries) == 1
        assert user.journal_entries[0].emotion == "gratitude"

        # Verify we can query related data
        gratitude_questions = db_session.query(GratitudeQuestion).all()
        emotion_questions = (
            db_session.query(EmotionQuestion)
            .filter(EmotionQuestion.emotion == "gratitude")
            .all()
        )
        quotes = db_session.query(Quote).filter(Quote.emotion == "gratitude").all()

        assert len(gratitude_questions) >= 1
        assert len(emotion_questions) >= 1
        assert len(quotes) >= 1
