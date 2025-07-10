from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import uvicorn
import random

from database import SessionLocal, engine, Base
from models import JournalEntry, GratitudeQuestion, EmotionQuestion, Quote, User
from schemas import (
    JournalEntryCreate,
    JournalEntryResponse,
    EmotionQuestionResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from emotion_data import EMOTION_QUESTIONS, QUOTES_DATA, GRATITUDE_QUESTIONS
from auth import get_current_user, get_current_user_dev

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carolina's Diary", description="A personalized journaling app")

# CORS middleware with improved security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://carolinas-diary.netlify.app",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"],  # Expose session ID header
)


# Dependency to get database session
def get_db():
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
                    db_question = EmotionQuestion(emotion=emotion, question=question)
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
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Welcome to Carolina's Diary"}


# User management endpoints
@app.post("/users/register", response_model=UserResponse)
async def register_user(
    user_data: dict = Depends(get_current_user_dev), db: Session = Depends(get_db)
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
    user_data: dict = Depends(get_current_user_dev), db: Session = Depends(get_db)
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
async def get_emotion_questions(emotion: str, db: Session = Depends(get_db)):
    """Get questions for a specific emotion"""
    questions = (
        db.query(EmotionQuestion).filter(EmotionQuestion.emotion == emotion).all()
    )
    return [EmotionQuestionResponse(id=q.id, question=q.question) for q in questions]


@app.get("/quote/{emotion}")
async def get_quote_for_emotion(emotion: str, db: Session = Depends(get_db)):
    """Get a random quote for a specific emotion"""
    quotes = db.query(Quote).filter(Quote.emotion == emotion).all()
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
        existing_entry.emotion = entry.emotion
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
            emotion=entry.emotion,
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
    # Validate date format and range to prevent injection
    if not entry_date or len(entry_date) != 10:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Check for valid characters only (digits and hyphens)
    if not all(c.isdigit() or c == '-' for c in entry_date):
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    try:
        entry_date_obj = datetime.strptime(entry_date, "%Y-%m-%d").date()
        
        # Validate date range (reasonable bounds)
        min_date = date(1900, 1, 1)
        max_date = date(2100, 12, 31)
        if entry_date_obj < min_date or entry_date_obj > max_date:
            raise HTTPException(
                status_code=400, detail="Date out of valid range (1900-2100)"
            )

        # Get current user
        user = get_user_by_firebase_uid(db, user_data["uid"])

        entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.date == entry_date_obj, JournalEntry.user_id == user.id
            )
            .first()
        )

        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        return entry
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )


@app.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_all_journal_entries(
    user_data: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all journal entries for the current user"""
    # Get current user
    user = get_user_by_firebase_uid(db, user_data["uid"])

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user.id)
        .order_by(JournalEntry.date.desc())
        .all()
    )
    return entries


@app.get("/emotions")
async def get_available_emotions():
    """Get list of available emotions"""
    return list(EMOTION_QUESTIONS.keys())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
