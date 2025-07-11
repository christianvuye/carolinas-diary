import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models import User, JournalEntry

class AnalyticsService:
    def __init__(self):
        self.posthog_api_key = os.getenv('POSTHOG_API_KEY', 'phc_test_key')
        self.posthog_host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
        self.api_url = f"{self.posthog_host}/capture"
        
    def track_event(self, event_name: str, properties: Dict[str, Any], user_id: Optional[str] = None):
        """Track an event to PostHog"""
        try:
            payload = {
                "api_key": self.posthog_api_key,
                "event": event_name,
                "properties": {
                    "timestamp": datetime.now().isoformat(),
                    "server_side": True,
                    **properties
                }
            }
            
            if user_id:
                payload["properties"]["distinct_id"] = user_id
                
            response = requests.post(self.api_url, json=payload, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error tracking event to PostHog: {e}")
            return False
    
    def identify_user(self, user_id: str, properties: Dict[str, Any]):
        """Identify a user in PostHog"""
        try:
            payload = {
                "api_key": self.posthog_api_key,
                "event": "$identify",
                "properties": {
                    "distinct_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "server_side": True,
                    **properties
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error identifying user in PostHog: {e}")
            return False
    
    def track_user_registration(self, user: User):
        """Track user registration event"""
        self.track_event("user_registered", {
            "user_id": user.firebase_uid,
            "email": user.email,
            "registration_date": user.created_at.isoformat() if user.created_at else None,
            "email_verified": user.email_verified,
        }, user.firebase_uid)
        
        # Identify the user
        self.identify_user(user.firebase_uid, {
            "email": user.email,
            "name": user.name,
            "registration_date": user.created_at.isoformat() if user.created_at else None,
            "email_verified": user.email_verified,
        })
    
    def track_journal_entry_created(self, entry: JournalEntry, user: User):
        """Track journal entry creation"""
        entry_length = self._calculate_entry_length(entry)
        
        self.track_event("journal_entry_created", {
            "entry_id": entry.id,
            "user_id": user.firebase_uid,
            "entry_date": entry.date.isoformat() if entry.date else None,
            "entry_length": entry_length,
            "has_gratitude": bool(entry.gratitude_answers and any(entry.gratitude_answers)),
            "has_emotion": bool(entry.emotion),
            "has_custom_text": bool(entry.custom_text),
            "gratitude_count": len([a for a in entry.gratitude_answers if a]) if entry.gratitude_answers else 0,
            "emotion_answers_count": len(entry.emotion_answers) if entry.emotion_answers else 0,
            "time_of_day": self._get_time_of_day(),
            "day_of_week": self._get_day_of_week(),
        }, user.firebase_uid)
    
    def track_journal_entry_updated(self, entry: JournalEntry, user: User):
        """Track journal entry update"""
        entry_length = self._calculate_entry_length(entry)
        
        self.track_event("journal_entry_updated", {
            "entry_id": entry.id,
            "user_id": user.firebase_uid,
            "entry_date": entry.date.isoformat() if entry.date else None,
            "entry_length": entry_length,
            "has_gratitude": bool(entry.gratitude_answers and any(entry.gratitude_answers)),
            "has_emotion": bool(entry.emotion),
            "has_custom_text": bool(entry.custom_text),
            "gratitude_count": len([a for a in entry.gratitude_answers if a]) if entry.gratitude_answers else 0,
            "emotion_answers_count": len(entry.emotion_answers) if entry.emotion_answers else 0,
            "time_of_day": self._get_time_of_day(),
            "day_of_week": self._get_day_of_week(),
        }, user.firebase_uid)
    
    def track_user_activity(self, user: User, db: Session):
        """Track user activity metrics"""
        # Get user's entry statistics
        total_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user.id,
            JournalEntry.created_at >= week_ago
        ).count()
        
        # Get streak information
        streak_days = self._calculate_streak(user, db)
        
        # Track daily active user
        self.track_event("daily_active_user", {
            "user_id": user.firebase_uid,
            "total_entries": total_entries,
            "recent_entries_7d": recent_entries,
            "streak_days": streak_days,
            "date": datetime.now().date().isoformat(),
        }, user.firebase_uid)
        
        # Update user properties
        self.identify_user(user.firebase_uid, {
            "total_entries": total_entries,
            "recent_entries_7d": recent_entries,
            "streak_days": streak_days,
            "last_activity": datetime.now().isoformat(),
        })
    
    def track_retention_metrics(self, user: User, db: Session):
        """Track user retention metrics"""
        if not user.created_at:
            return
            
        days_since_registration = (datetime.now() - user.created_at).days
        
        # Get retention cohort
        retention_cohort = self._get_retention_cohort(days_since_registration)
        
        # Get total entries for this user
        total_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()
        
        self.track_event("user_retention", {
            "user_id": user.firebase_uid,
            "days_since_registration": days_since_registration,
            "retention_cohort": retention_cohort,
            "total_entries": total_entries,
            "registration_date": user.created_at.isoformat(),
        }, user.firebase_uid)
    
    def track_feature_usage(self, feature_name: str, user_id: str, properties: Optional[Dict[str, Any]] = None):
        """Track feature usage"""
        self.track_event("feature_used", {
            "feature_name": feature_name,
            "time_of_day": self._get_time_of_day(),
            "day_of_week": self._get_day_of_week(),
            **(properties or {})
        }, user_id)
    
    def track_error(self, error_type: str, error_message: str, user_id: Optional[str] = None):
        """Track error events"""
        self.track_event("error_occurred", {
            "error_type": error_type,
            "error_message": error_message,
            "server_side": True,
        }, user_id)
    
    def track_performance(self, metric: str, value: float, user_id: Optional[str] = None):
        """Track performance metrics"""
        self.track_event("performance_metric", {
            "metric": metric,
            "value": value,
            "server_side": True,
        }, user_id)
    
    def _calculate_entry_length(self, entry: JournalEntry) -> int:
        """Calculate the total length of a journal entry"""
        total_length = 0
        
        # Calculate gratitude answers length
        if entry.gratitude_answers:
            total_length += sum(len(answer) for answer in entry.gratitude_answers if answer)
        
        # Calculate emotion answers length
        if entry.emotion_answers:
            total_length += sum(len(answer) for answer in entry.emotion_answers if answer)
        
        # Add custom text length
        if entry.custom_text:
            total_length += len(entry.custom_text)
        
        return total_length
    
    def _calculate_streak(self, user: User, db: Session) -> int:
        """Calculate user's current streak of consecutive days with entries"""
        if not user.created_at:
            return 0
            
        # Get all entry dates for this user
        entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()
        entry_dates = {entry.date.date() for entry in entries if entry.date}
        
        if not entry_dates:
            return 0
        
        # Calculate streak
        current_date = datetime.now().date()
        streak = 0
        
        while current_date in entry_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    def _get_time_of_day(self) -> str:
        """Get current time of day category"""
        hour = datetime.now().hour
        if hour < 6:
            return "early_morning"
        elif hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        elif hour < 21:
            return "evening"
        else:
            return "night"
    
    def _get_day_of_week(self) -> str:
        """Get current day of week"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        return days[datetime.now().weekday()]
    
    def _get_retention_cohort(self, days: int) -> str:
        """Get retention cohort based on days since registration"""
        if days <= 1:
            return "day_1"
        elif days <= 7:
            return "week_1"
        elif days <= 30:
            return "month_1"
        elif days <= 90:
            return "month_3"
        else:
            return "month_6_plus"

# Create singleton instance
analytics_service = AnalyticsService()