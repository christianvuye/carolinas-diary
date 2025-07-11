from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from models import (
    User, UserSession, FeatureUsage, UserRetention, 
    DailyActiveUsers, WeeklyActiveUsers, MonthlyActiveUsers,
    EntryCompletionMetrics, JournalEntry
)
import json


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def start_session(self, user_id: int, ip_address: str = None, 
                     user_agent: str = None, device_type: str = None) -> UserSession:
        """Start a new user session"""
        session = UserSession(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_session(self, session_id: int) -> None:
        """End a user session and calculate duration"""
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
        if session and not session.session_end:
            session.session_end = datetime.utcnow()
            session.duration_seconds = (session.session_end - session.session_start).total_seconds()
            self.db.commit()

    def track_feature_usage(self, user_id: int, feature_name: str, 
                           session_id: Optional[int] = None,
                           feature_data: Dict[str, Any] = None,
                           duration_seconds: Optional[float] = None) -> FeatureUsage:
        """Track feature usage"""
        usage = FeatureUsage(
            user_id=user_id,
            session_id=session_id,
            feature_name=feature_name,
            feature_data=feature_data,
            duration_seconds=duration_seconds
        )
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        return usage

    def track_journal_entry(self, user_id: int, entry_data: Dict[str, Any], 
                           session_id: Optional[int] = None,
                           completion_time: Optional[float] = None) -> JournalEntry:
        """Track journal entry creation with analytics data"""
        # Calculate entry length
        entry_length = 0
        if entry_data.get('custom_text'):
            entry_length += len(entry_data['custom_text'])
        if entry_data.get('gratitude_answers'):
            entry_length += sum(len(str(answer)) for answer in entry_data['gratitude_answers'])
        if entry_data.get('emotion_answers'):
            entry_length += sum(len(str(answer)) for answer in entry_data['emotion_answers'])

        entry = JournalEntry(
            user_id=user_id,
            date=entry_data.get('date', date.today()),
            gratitude_answers=entry_data.get('gratitude_answers'),
            emotion=entry_data.get('emotion'),
            emotion_answers=entry_data.get('emotion_answers'),
            custom_text=entry_data.get('custom_text'),
            visual_settings=entry_data.get('visual_settings'),
            entry_length=entry_length,
            completion_time=completion_time,
            is_completed=bool(entry_data.get('custom_text') or entry_data.get('gratitude_answers')),
            session_id=session_id
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def calculate_daily_metrics(self, target_date: date = None) -> DailyActiveUsers:
        """Calculate daily active users and related metrics"""
        if target_date is None:
            target_date = date.today()

        # Check if metrics already exist for this date
        existing = self.db.query(DailyActiveUsers).filter(
            DailyActiveUsers.date == target_date
        ).first()
        if existing:
            return existing

        # Calculate active users
        active_users = self.db.query(UserSession.user_id).filter(
            func.date(UserSession.session_start) == target_date
        ).distinct().count()

        # Calculate new users
        new_users = self.db.query(User.id).filter(
            func.date(User.created_at) == target_date
        ).count()

        # Calculate returning users
        returning_users = active_users - new_users

        # Calculate total sessions
        total_sessions = self.db.query(UserSession).filter(
            func.date(UserSession.session_start) == target_date
        ).count()

        # Calculate average session duration
        avg_duration = self.db.query(func.avg(UserSession.duration_seconds)).filter(
            and_(
                func.date(UserSession.session_start) == target_date,
                UserSession.duration_seconds.isnot(None)
            )
        ).scalar() or 0.0

        daily_metrics = DailyActiveUsers(
            date=target_date,
            active_users=active_users,
            new_users=new_users,
            returning_users=returning_users,
            total_sessions=total_sessions,
            avg_session_duration=avg_duration
        )
        self.db.add(daily_metrics)
        self.db.commit()
        self.db.refresh(daily_metrics)
        return daily_metrics

    def calculate_weekly_metrics(self, week_start: date = None) -> WeeklyActiveUsers:
        """Calculate weekly active users and related metrics"""
        if week_start is None:
            # Get the start of the current week (Monday)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        # Check if metrics already exist
        existing = self.db.query(WeeklyActiveUsers).filter(
            WeeklyActiveUsers.week_start == week_start
        ).first()
        if existing:
            return existing

        week_end = week_start + timedelta(days=6)

        # Calculate active users
        active_users = self.db.query(UserSession.user_id).filter(
            and_(
                func.date(UserSession.session_start) >= week_start,
                func.date(UserSession.session_start) <= week_end
            )
        ).distinct().count()

        # Calculate new users
        new_users = self.db.query(User.id).filter(
            and_(
                func.date(User.created_at) >= week_start,
                func.date(User.created_at) <= week_end
            )
        ).count()

        # Calculate returning users
        returning_users = active_users - new_users

        # Calculate total sessions
        total_sessions = self.db.query(UserSession).filter(
            and_(
                func.date(UserSession.session_start) >= week_start,
                func.date(UserSession.session_start) <= week_end
            )
        ).count()

        # Calculate average session duration
        avg_duration = self.db.query(func.avg(UserSession.duration_seconds)).filter(
            and_(
                func.date(UserSession.session_start) >= week_start,
                func.date(UserSession.session_start) <= week_end,
                UserSession.duration_seconds.isnot(None)
            )
        ).scalar() or 0.0

        weekly_metrics = WeeklyActiveUsers(
            week_start=week_start,
            active_users=active_users,
            new_users=new_users,
            returning_users=returning_users,
            total_sessions=total_sessions,
            avg_session_duration=avg_duration
        )
        self.db.add(weekly_metrics)
        self.db.commit()
        self.db.refresh(weekly_metrics)
        return weekly_metrics

    def calculate_monthly_metrics(self, month_start: date = None) -> MonthlyActiveUsers:
        """Calculate monthly active users and related metrics"""
        if month_start is None:
            # Get the start of the current month
            today = date.today()
            month_start = today.replace(day=1)

        # Check if metrics already exist
        existing = self.db.query(MonthlyActiveUsers).filter(
            MonthlyActiveUsers.month_start == month_start
        ).first()
        if existing:
            return existing

        # Calculate next month start
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)

        # Calculate active users
        active_users = self.db.query(UserSession.user_id).filter(
            and_(
                func.date(UserSession.session_start) >= month_start,
                func.date(UserSession.session_start) <= month_end
            )
        ).distinct().count()

        # Calculate new users
        new_users = self.db.query(User.id).filter(
            and_(
                func.date(User.created_at) >= month_start,
                func.date(User.created_at) <= month_end
            )
        ).count()

        # Calculate returning users
        returning_users = active_users - new_users

        # Calculate total sessions
        total_sessions = self.db.query(UserSession).filter(
            and_(
                func.date(UserSession.session_start) >= month_start,
                func.date(UserSession.session_start) <= month_end
            )
        ).count()

        # Calculate average session duration
        avg_duration = self.db.query(func.avg(UserSession.duration_seconds)).filter(
            and_(
                func.date(UserSession.session_start) >= month_start,
                func.date(UserSession.session_start) <= month_end,
                UserSession.duration_seconds.isnot(None)
            )
        ).scalar() or 0.0

        monthly_metrics = MonthlyActiveUsers(
            month_start=month_start,
            active_users=active_users,
            new_users=new_users,
            returning_users=returning_users,
            total_sessions=total_sessions,
            avg_session_duration=avg_duration
        )
        self.db.add(monthly_metrics)
        self.db.commit()
        self.db.refresh(monthly_metrics)
        return monthly_metrics

    def calculate_entry_completion_metrics(self, target_date: date = None) -> EntryCompletionMetrics:
        """Calculate journal entry completion metrics"""
        if target_date is None:
            target_date = date.today()

        # Check if metrics already exist
        existing = self.db.query(EntryCompletionMetrics).filter(
            EntryCompletionMetrics.date == target_date
        ).first()
        if existing:
            return existing

        # Calculate metrics
        entries_started = self.db.query(JournalEntry).filter(
            func.date(JournalEntry.created_at) == target_date
        ).count()

        entries_completed = self.db.query(JournalEntry).filter(
            and_(
                func.date(JournalEntry.created_at) == target_date,
                JournalEntry.is_completed == True
            )
        ).count()

        completion_rate = (entries_completed / entries_started * 100) if entries_started > 0 else 0.0

        # Calculate average completion time
        avg_completion_time = self.db.query(func.avg(JournalEntry.completion_time)).filter(
            and_(
                func.date(JournalEntry.created_at) == target_date,
                JournalEntry.completion_time.isnot(None)
            )
        ).scalar() or 0.0

        # Calculate average entry length
        avg_entry_length = self.db.query(func.avg(JournalEntry.entry_length)).filter(
            func.date(JournalEntry.created_at) == target_date
        ).scalar() or 0.0

        completion_metrics = EntryCompletionMetrics(
            date=target_date,
            total_entries_started=entries_started,
            total_entries_completed=entries_completed,
            completion_rate=completion_rate,
            avg_completion_time=avg_completion_time,
            avg_entry_length=avg_entry_length
        )
        self.db.add(completion_metrics)
        self.db.commit()
        self.db.refresh(completion_metrics)
        return completion_metrics

    def get_user_retention_curve(self, cohort_date: date, days_to_track: int = 30) -> Dict[int, float]:
        """Calculate retention curve for a specific cohort"""
        retention_data = {}
        
        for day in range(days_to_track + 1):
            retention_date = cohort_date + timedelta(days=day)
            
            # Get users in this cohort
            cohort_users = self.db.query(User.id).filter(
                func.date(User.created_at) == cohort_date
            ).subquery()
            
            # Count retained users
            retained_users = self.db.query(UserSession.user_id).filter(
                and_(
                    UserSession.user_id.in_(cohort_users),
                    func.date(UserSession.session_start) == retention_date
                )
            ).distinct().count()
            
            # Count total cohort size
            total_cohort = self.db.query(User).filter(
                func.date(User.created_at) == cohort_date
            ).count()
            
            retention_rate = (retained_users / total_cohort * 100) if total_cohort > 0 else 0.0
            retention_data[day] = retention_rate
            
        return retention_data

    def get_feature_usage_patterns(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get feature usage patterns"""
        if start_date is None:
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()

        # Get feature usage counts
        feature_usage = self.db.query(
            FeatureUsage.feature_name,
            func.count(FeatureUsage.id).label('usage_count'),
            func.avg(FeatureUsage.duration_seconds).label('avg_duration')
        ).filter(
            and_(
                func.date(FeatureUsage.usage_time) >= start_date,
                func.date(FeatureUsage.usage_time) <= end_date
            )
        ).group_by(FeatureUsage.feature_name).all()

        # Get usage by time of day
        hourly_usage = self.db.query(
            extract('hour', FeatureUsage.usage_time).label('hour'),
            func.count(FeatureUsage.id).label('usage_count')
        ).filter(
            and_(
                func.date(FeatureUsage.usage_time) >= start_date,
                func.date(FeatureUsage.usage_time) <= end_date
            )
        ).group_by(extract('hour', FeatureUsage.usage_time)).all()

        return {
            'feature_usage': [{'feature': f.feature_name, 'count': f.usage_count, 'avg_duration': f.avg_duration} for f in feature_usage],
            'hourly_usage': [{'hour': h.hour, 'count': h.usage_count} for h in hourly_usage]
        }