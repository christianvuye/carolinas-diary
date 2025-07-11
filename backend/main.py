"""FastAPI backend application for Carolina's Diary journaling app."""

import random
from datetime import date, datetime
import uvicorn
from auth import get_current_user, get_current_user_dev
from database import Base, SessionLocal, engine
from emotion_data import EMOTION_QUESTIONS, GRATITUDE_QUESTIONS, QUOTES_DATA
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import EmotionQuestion, GratitudeQuestion, JournalEntry, Quote, User
from schemas import (
    Emotion,
    EmotionQuestionResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    PaginatedJournalEntriesResponse,
    PaginationMetadata,
    UserResponse,
    UserUpdate,
)
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from sqlalchemy.orm import Session

# flake8: noqa: E501

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Carolina's Diary",
    description="A personalized journaling app",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database session
def get_db():
    """
    Provides a generator for database session handling, ensuring the session
    is properly opened and closed.
    Parameters:
        None
    Returns:
        - generator: A context manager that yields a SQLAlchemy database
        session.
    Example:
        - Using the FastAPI dependency injection, a route can access the
        database session as follows:
          @app.get("/items/")
          def read_items(db: Session = Depends(get_db)):
              return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to get user from database
def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> User:
    """Get user by Firebase UID, create if doesn't exist"""
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found. Please register first."
        )
    return user


# Initialize database with questions and quotes
@app.on_event("startup")
async def startup_event():
    """Initialize database with questions and quotes on startup."""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(GratitudeQuestion).count() == 0:
            # Add gratitude questions
            for question in GRATITUDE_QUESTIONS:
                db_question = GratitudeQuestion(question=question)
                db.add(db_question)

        if db.query(EmotionQuestion).count() == 0:
            # Add emotion questions
            for emotion, questions in EMOTION_QUESTIONS.items():
                for question in questions:
                    db_question = EmotionQuestion(
                        emotion=emotion,
                        question=question,
                    )
                    db.add(db_question)

        if db.query(Quote).count() == 0:
            # Add quotes
            for emotion, quotes in QUOTES_DATA.items():
                for quote_data in quotes:
                    db_quote = Quote(
                        emotion=emotion,
                        quote=quote_data["quote"],
                        author=quote_data["author"],
                    )
                    db.add(db_quote)

        db.commit()
    except (SQLAlchemyError, DatabaseError) as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()


@app.get("/")
async def root():
    """
    Serves as the root endpoint, providing a welcome message.
    Returns:
        - dict: A dictionary containing a welcome message.
    Example:
        - root() -> {"message": "Welcome to Carolina's Diary"}
    """
    return {"message": "Welcome to Carolina's Diary"}


# User management endpoints
@app.post("/users/register", response_model=UserResponse)
async def register_user(
    user_data: dict = Depends(get_current_user_dev),
    db: Session = Depends(get_db),
):
    """
    Register a new user or return existing user
    """
    existing_user = db.query(User).filter(User.firebase_uid == user_data["uid"]).first()

    if existing_user:
        return existing_user

    new_user = User(
        firebase_uid=user_data["uid"],
        email=user_data["email"],
        name=user_data.get("name"),
        picture=user_data.get("picture"),
        email_verified=user_data.get("email_verified", False),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    user_data: dict = Depends(get_current_user_dev),
    db: Session = Depends(get_db),
):
    """
    Get current user information
    """
    user = db.query(User).filter(User.firebase_uid == user_data["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    user_data: dict = Depends(get_current_user_dev),
    db: Session = Depends(get_db),
):
    """
    Update current user information
    """
    user = db.query(User).filter(User.firebase_uid == user_data["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.picture is not None:
        user.picture = user_update.picture
    if user_update.email_verified is not None:
        user.email_verified = user_update.email_verified
    if user_update.preferences is not None:
        user.preferences = user_update.preferences

    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)

    return user


@app.get("/gratitude-questions")
async def get_gratitude_questions(db: Session = Depends(get_db)):
    """Get 5 random gratitude questions for today"""
    questions = db.query(GratitudeQuestion).all()
    if len(questions) < 5:
        return [q.question for q in questions]
    return [q.question for q in random.sample(questions, 5)]


@app.get("/emotion-questions/{emotion}")
async def get_emotion_questions(emotion: Emotion, db: Session = Depends(get_db)):
    """Get questions for a specific emotion"""
    questions = (
        db.query(EmotionQuestion).filter(EmotionQuestion.emotion == emotion.value).all()
    )
    return [EmotionQuestionResponse(id=q.id, question=q.question) for q in questions]


@app.get("/quote/{emotion}")
async def get_quote_for_emotion(emotion: Emotion, db: Session = Depends(get_db)):
    """Get a random quote for a specific emotion"""
    quotes = db.query(Quote).filter(Quote.emotion == emotion.value).all()
    if not quotes:
        return {"quote": "Every day is a new beginning.", "author": "Unknown"}
    selected_quote = random.choice(quotes)
    return {"quote": selected_quote.quote, "author": selected_quote.author}


@app.post("/journal-entry", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update a journal entry for today"""
    today = date.today()

    # Get current user
    user = get_user_by_firebase_uid(db, user_data["uid"])

    # Check if entry exists for today for this user
    existing_entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.date == today, JournalEntry.user_id == user.id)
        .first()
    )

    if existing_entry:
        # Update existing entry
        existing_entry.gratitude_answers = entry.gratitude_answers
        existing_entry.emotion = entry.emotion.value if entry.emotion else None
        existing_entry.emotion_answers = entry.emotion_answers
        existing_entry.custom_text = entry.custom_text
        existing_entry.visual_settings = entry.visual_settings
        existing_entry.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_entry)
        return existing_entry
    else:
        # Create new entry
        db_entry = JournalEntry(
            user_id=user.id,
            date=today,
            gratitude_answers=entry.gratitude_answers,
            emotion=entry.emotion.value if entry.emotion else None,
            emotion_answers=entry.emotion_answers,
            custom_text=entry.custom_text,
            visual_settings=entry.visual_settings,
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry


@app.get("/journal-entry/{entry_date}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_date: str,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get journal entry for a specific date"""
    try:
        entry_date_obj = datetime.strptime(entry_date, "%Y-%m-%d").date()

        # Get current user
        user = get_user_by_firebase_uid(db, user_data["uid"])

        entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.date == entry_date_obj,
                JournalEntry.user_id == user.id,
            )
            .first()
        )

        if not entry:
            raise HTTPException(
                status_code=404,
                detail="Journal entry not found",
            )
        return entry
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        ) from exc


@app.get("/journal-entries", response_model=PaginatedJournalEntriesResponse)
async def get_all_journal_entries(
    page: int = 1,
    page_size: int = 10,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated journal entries for the current user

    Args:
        page: Page number (starts from 1)
        page_size: Number of entries per page (max 100)
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400, detail="Page size must be between 1 and 100"
        )

    # Get current user
    user = get_user_by_firebase_uid(db, user_data["uid"])

    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count for pagination metadata
    total_items = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()

    # Get paginated entries
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user.id)
        .order_by(JournalEntry.date.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Calculate pagination metadata
    total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
    has_next = page < total_pages
    has_previous = page > 1

    pagination_metadata = PaginationMetadata(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_items=total_items,
        has_next=has_next,
        has_previous=has_previous,
    )

    return PaginatedJournalEntriesResponse(
        entries=[JournalEntryResponse.model_validate(entry) for entry in entries],
        pagination=pagination_metadata,
    )


@app.get("/emotions")
async def get_available_emotions():
    """Get list of available emotions"""
    return [emotion.value for emotion in Emotion]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
