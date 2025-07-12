#!/usr/bin/env python3
"""
Database initialization script for Carolina's Diary
Creates all tables and populates with initial data
"""

# flake8: noqa: E501

from database import Base, engine
from models import EmotionQuestion, GratitudeQuestion, Quote
from sqlalchemy.orm import sessionmaker

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize the database with all tables and initial data"""
    print("Initializing database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_questions = db.query(GratitudeQuestion).count()
        if existing_questions > 0:
            print("Database already contains data. Skipping initialization.")
            return

        # Add gratitude questions
        gratitude_questions = [
            "What made you smile today?",
            "Who are you grateful for and why?",
            "What is something beautiful you noticed today?",
            "What is a small victory you experienced today?",
            "What comfort are you grateful for today?",
            "What did you learn about yourself today?",
            "What act of kindness did you witness or experience?",
            "What challenge helped you grow today?",
            "What memory brought you joy today?",
            "What opportunity are you grateful for?",
        ]

        for question in gratitude_questions:
            db.add(GratitudeQuestion(question=question))

        # Add emotion questions
        emotion_questions = [
            # Anxiety
            (
                "anxiety",
                "What specific thoughts or situations triggered your anxiety today?",
            ),
            (
                "anxiety",
                "What physical sensations did you notice when feeling anxious?",
            ),
            (
                "anxiety",
                "What coping strategies helped you manage your anxiety?",
            ),
            (
                "anxiety",
                "What would you tell a friend experiencing similar anxiety?",
            ),
            # Sadness
            (
                "sadness",
                "What is at the root of your sadness today?",
            ),
            (
                "sadness",
                "How has this sadness affected your day?",
            ),
            (
                "sadness",
                "What small thing could bring you comfort right now?",
            ),
            (
                "sadness",
                "What support do you need during this difficult time?",
            ),
            # Stress
            (
                "stress",
                "What are the main sources of stress in your life right now?",
            ),
            (
                "stress",
                "How is stress showing up in your body and mind?",
            ),
            (
                "stress",
                "What boundaries could you set to reduce stress?",
            ),
            (
                "stress",
                "What would help you feel more balanced?",
            ),
            # Happiness
            (
                "happiness",
                "What brought you the most joy today?",
            ),
            (
                "happiness",
                "How did you share your happiness with others?",
            ),
            (
                "happiness",
                "What do you want to remember about this feeling?",
            ),
            (
                "happiness",
                "How can you cultivate more moments like this?",
            ),
            # Anger
            (
                "anger",
                "What situation or person triggered your anger?",
            ),
            (
                "anger",
                "What underlying need or value was not being honored?",
            ),
            (
                "anger",
                "How can you express this anger constructively?",
            ),
            (
                "anger",
                "What would resolution look like for you?",
            ),
        ]

        for emotion, question in emotion_questions:
            db.add(EmotionQuestion(emotion=emotion, question=question))

        # Add quotes
        quotes = [
            (
                "anxiety",
                "You are braver than you believe, stronger than you seem, and smarter than you think.",  # noqa: E501
                "A.A. Milne",
            ),
            (
                "anxiety",
                "Nothing can bring you peace but yourself.",
                "Ralph Waldo Emerson",
            ),
            (
                "sadness",
                "The wound is the place where the Light enters you.",
                "Rumi",
            ),
            (
                "sadness",
                "Grief is the price we pay for love.",
                "Queen Elizabeth II",
            ),
            (
                "stress",
                "You have been assigned this mountain to show others it can be moved.",
                "Mel Robbins",
            ),
            (
                "stress",
                "Take time to make your soul happy.",
                "Unknown",
            ),
            (
                "happiness",
                "Happiness is not something ready made. It comes from your own actions.",
                "Dalai Lama",
            ),
            (
                "happiness",
                "The secret of being happy is accepting where you are in life.",
                "Unknown",
            ),
            (
                "anger",
                "For every minute you are angry you lose sixty seconds of happiness.",
                "Ralph Waldo Emerson",
            ),
            (
                "anger",
                "Anger is an acid that can do more harm to the vessel in which it is stored than to anything on which it is poured.",  # noqa: E501
                "Mark Twain",
            ),
        ]

        for emotion, quote_text, author in quotes:
            db.add(Quote(emotion=emotion, quote=quote_text, author=author))

        # Commit all changes
        db.commit()

        print("✅ Database initialized with initial data")
        print(f"   - {len(gratitude_questions)} gratitude questions")
        print(f"   - {len(emotion_questions)} emotion questions")
        print(f"   - {len(quotes)} quotes")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    init_database()
    print("\n🎉 Database initialization completed!")


if __name__ == "__main__":
    main()
