#!/usr/bin/env python3
"""
Test script for analytics functionality.
This script tests the analytics endpoints and database connections.
"""

import requests
import json
from datetime import datetime, date, timedelta
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

def test_session_tracking():
    """Test session tracking functionality"""
    print("🧪 Testing session tracking...")
    
    # Start session
    headers = {"X-User-ID": TEST_USER_ID}
    response = requests.post(f"{BASE_URL}/analytics/session/start", headers=headers)
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data.get("session_id")
        print(f"✅ Session started: {session_id}")
        
        # Wait a bit
        time.sleep(2)
        
        # End session
        response = requests.post(f"{BASE_URL}/analytics/session/end/{session_id}")
        if response.status_code == 200:
            print("✅ Session ended successfully")
        else:
            print(f"❌ Failed to end session: {response.status_code}")
    else:
        print(f"❌ Failed to start session: {response.status_code}")

def test_feature_usage():
    """Test feature usage tracking"""
    print("🧪 Testing feature usage tracking...")
    
    headers = {"X-User-ID": TEST_USER_ID}
    data = {
        "feature_name": "journal_prompt",
        "feature_data": {"prompt_type": "gratitude", "prompt_id": 1},
        "duration_seconds": 45.2
    }
    
    response = requests.post(f"{BASE_URL}/analytics/feature/usage", 
                           headers=headers, json=data)
    
    if response.status_code == 200:
        usage_data = response.json()
        print(f"✅ Feature usage tracked: {usage_data.get('usage_id')}")
    else:
        print(f"❌ Failed to track feature usage: {response.status_code}")

def test_journal_entry_tracking():
    """Test journal entry tracking"""
    print("🧪 Testing journal entry tracking...")
    
    headers = {"X-User-ID": TEST_USER_ID}
    entry_data = {
        "date": date.today().isoformat(),
        "gratitude_answers": ["I'm grateful for my health", "I'm grateful for my family"],
        "emotion": "happy",
        "emotion_answers": ["I feel content today"],
        "custom_text": "Today was a wonderful day filled with joy and laughter.",
        "visual_settings": {"theme": "warm", "font": "serif"}
    }
    
    response = requests.post(f"{BASE_URL}/analytics/journal/entry", 
                           headers=headers, json=entry_data)
    
    if response.status_code == 200:
        entry_data = response.json()
        print(f"✅ Journal entry tracked: {entry_data.get('entry_id')}")
        print(f"   Entry length: {entry_data.get('entry_length')} characters")
        print(f"   Completed: {entry_data.get('is_completed')}")
    else:
        print(f"❌ Failed to track journal entry: {response.status_code}")

def test_metrics_retrieval():
    """Test metrics retrieval"""
    print("🧪 Testing metrics retrieval...")
    
    # Test daily metrics
    response = requests.get(f"{BASE_URL}/analytics/metrics/daily")
    if response.status_code == 200:
        metrics = response.json()
        print(f"✅ Daily metrics retrieved:")
        print(f"   Active users: {metrics.get('active_users')}")
        print(f"   New users: {metrics.get('new_users')}")
        print(f"   Total sessions: {metrics.get('total_sessions')}")
    else:
        print(f"❌ Failed to get daily metrics: {response.status_code}")
    
    # Test completion metrics
    response = requests.get(f"{BASE_URL}/analytics/metrics/completion")
    if response.status_code == 200:
        metrics = response.json()
        print(f"✅ Completion metrics retrieved:")
        print(f"   Completion rate: {metrics.get('completion_rate')}%")
        print(f"   Avg completion time: {metrics.get('avg_completion_time')} seconds")
    else:
        print(f"❌ Failed to get completion metrics: {response.status_code}")

def test_retention_analysis():
    """Test retention analysis"""
    print("🧪 Testing retention analysis...")
    
    # Use a recent date for testing
    test_date = (date.today() - timedelta(days=7)).isoformat()
    response = requests.get(f"{BASE_URL}/analytics/retention/curve?cohort_date={test_date}&days_to_track=7")
    
    if response.status_code == 200:
        retention_data = response.json()
        print(f"✅ Retention analysis retrieved:")
        print(f"   Cohort date: {retention_data.get('cohort_date')}")
        print(f"   Days tracked: {retention_data.get('days_to_track')}")
        curve = retention_data.get('retention_curve', {})
        if curve:
            print(f"   Day 0 retention: {curve.get('0', 0)}%")
            print(f"   Day 7 retention: {curve.get('7', 0)}%")
    else:
        print(f"❌ Failed to get retention analysis: {response.status_code}")

def test_feature_usage_patterns():
    """Test feature usage patterns"""
    print("🧪 Testing feature usage patterns...")
    
    response = requests.get(f"{BASE_URL}/analytics/usage/patterns")
    
    if response.status_code == 200:
        patterns = response.json()
        print(f"✅ Feature usage patterns retrieved:")
        feature_usage = patterns.get('feature_usage', [])
        print(f"   Features tracked: {len(feature_usage)}")
        for feature in feature_usage[:3]:  # Show first 3 features
            print(f"     {feature.get('feature')}: {feature.get('count')} uses")
    else:
        print(f"❌ Failed to get feature usage patterns: {response.status_code}")

def main():
    """Run all tests"""
    print("🎯 Testing Analytics System")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return
    
    # Run tests
    test_session_tracking()
    test_feature_usage()
    test_journal_entry_tracking()
    test_metrics_retrieval()
    test_retention_analysis()
    test_feature_usage_patterns()
    
    print("\n🎉 Analytics testing completed!")
    print("\n📊 To view your analytics data:")
    print("1. Access pgAdmin at http://localhost:8080")
    print("2. Login with admin@carolinasdiary.com / admin_password")
    print("3. Connect to the PostgreSQL database")
    print("4. Explore the analytics tables")

if __name__ == "__main__":
    main()