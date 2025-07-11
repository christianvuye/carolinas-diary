from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import date, datetime
from database import get_db
from analytics import AnalyticsService
from models import User
import json

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/session/start")
async def start_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """Start a new user session"""
    # Get user from request (assuming you have authentication middleware)
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    analytics = AnalyticsService(db)
    
    # Get client information
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    
    # Determine device type from user agent
    device_type = "desktop"
    if user_agent:
        user_agent_lower = user_agent.lower()
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            device_type = "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            device_type = "tablet"
    
    session = analytics.start_session(
        user_id=int(user_id),
        ip_address=ip_address,
        user_agent=user_agent,
        device_type=device_type
    )
    
    return {
        "session_id": session.id,
        "session_start": session.session_start.isoformat()
    }


@router.post("/session/end/{session_id}")
async def end_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """End a user session"""
    analytics = AnalyticsService(db)
    analytics.end_session(session_id)
    return {"message": "Session ended successfully"}


@router.post("/feature/usage")
async def track_feature_usage(
    feature_name: str,
    feature_data: Optional[Dict[str, Any]] = None,
    duration_seconds: Optional[float] = None,
    session_id: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Track feature usage"""
    user_id = request.headers.get("X-User-ID") if request else None
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    analytics = AnalyticsService(db)
    usage = analytics.track_feature_usage(
        user_id=int(user_id),
        feature_name=feature_name,
        session_id=session_id,
        feature_data=feature_data,
        duration_seconds=duration_seconds
    )
    
    return {
        "usage_id": usage.id,
        "feature_name": usage.feature_name,
        "usage_time": usage.usage_time.isoformat()
    }


@router.post("/journal/entry")
async def track_journal_entry(
    entry_data: Dict[str, Any],
    completion_time: Optional[float] = None,
    session_id: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Track journal entry creation with analytics"""
    user_id = request.headers.get("X-User-ID") if request else None
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    analytics = AnalyticsService(db)
    entry = analytics.track_journal_entry(
        user_id=int(user_id),
        entry_data=entry_data,
        session_id=session_id,
        completion_time=completion_time
    )
    
    return {
        "entry_id": entry.id,
        "entry_length": entry.entry_length,
        "is_completed": entry.is_completed,
        "completion_time": entry.completion_time
    }


@router.get("/metrics/daily")
async def get_daily_metrics(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get daily active users and related metrics"""
    analytics = AnalyticsService(db)
    
    if target_date:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        date_obj = None
    
    metrics = analytics.calculate_daily_metrics(date_obj)
    
    return {
        "date": metrics.date.isoformat(),
        "active_users": metrics.active_users,
        "new_users": metrics.new_users,
        "returning_users": metrics.returning_users,
        "total_sessions": metrics.total_sessions,
        "avg_session_duration": metrics.avg_session_duration
    }


@router.get("/metrics/weekly")
async def get_weekly_metrics(
    week_start: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get weekly active users and related metrics"""
    analytics = AnalyticsService(db)
    
    if week_start:
        date_obj = datetime.strptime(week_start, "%Y-%m-%d").date()
    else:
        date_obj = None
    
    metrics = analytics.calculate_weekly_metrics(date_obj)
    
    return {
        "week_start": metrics.week_start.isoformat(),
        "active_users": metrics.active_users,
        "new_users": metrics.new_users,
        "returning_users": metrics.returning_users,
        "total_sessions": metrics.total_sessions,
        "avg_session_duration": metrics.avg_session_duration
    }


@router.get("/metrics/monthly")
async def get_monthly_metrics(
    month_start: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get monthly active users and related metrics"""
    analytics = AnalyticsService(db)
    
    if month_start:
        date_obj = datetime.strptime(month_start, "%Y-%m-%d").date()
    else:
        date_obj = None
    
    metrics = analytics.calculate_monthly_metrics(date_obj)
    
    return {
        "month_start": metrics.month_start.isoformat(),
        "active_users": metrics.active_users,
        "new_users": metrics.new_users,
        "returning_users": metrics.returning_users,
        "total_sessions": metrics.total_sessions,
        "avg_session_duration": metrics.avg_session_duration
    }


@router.get("/metrics/completion")
async def get_completion_metrics(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get journal entry completion metrics"""
    analytics = AnalyticsService(db)
    
    if target_date:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        date_obj = None
    
    metrics = analytics.calculate_entry_completion_metrics(date_obj)
    
    return {
        "date": metrics.date.isoformat(),
        "total_entries_started": metrics.total_entries_started,
        "total_entries_completed": metrics.total_entries_completed,
        "completion_rate": metrics.completion_rate,
        "avg_completion_time": metrics.avg_completion_time,
        "avg_entry_length": metrics.avg_entry_length
    }


@router.get("/retention/curve")
async def get_retention_curve(
    cohort_date: str,
    days_to_track: int = 30,
    db: Session = Depends(get_db)
):
    """Get user retention curve for a specific cohort"""
    analytics = AnalyticsService(db)
    
    try:
        cohort_date_obj = datetime.strptime(cohort_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    retention_data = analytics.get_user_retention_curve(cohort_date_obj, days_to_track)
    
    return {
        "cohort_date": cohort_date,
        "days_to_track": days_to_track,
        "retention_curve": retention_data
    }


@router.get("/usage/patterns")
async def get_feature_usage_patterns(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get feature usage patterns"""
    analytics = AnalyticsService(db)
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    patterns = analytics.get_feature_usage_patterns(start_date_obj, end_date_obj)
    
    return patterns