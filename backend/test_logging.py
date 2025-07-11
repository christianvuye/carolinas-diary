#!/usr/bin/env python3
"""
Test script for database query logging system
"""

import time
from database import SessionLocal, get_query_performance_stats
from models import User, JournalEntry, GratitudeQuestion

def test_query_logging():
    """Test the query logging system with various database operations"""
    
    print("Testing Database Query Logging System")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Test 1: Simple SELECT queries
        print("\n1. Testing SELECT queries...")
        users = db.query(User).all()
        print(f"   Found {len(users)} users")
        
        questions = db.query(GratitudeQuestion).all()
        print(f"   Found {len(questions)} gratitude questions")
        
        # Test 2: Filtered queries
        print("\n2. Testing filtered queries...")
        if users:
            user = db.query(User).filter(User.id == users[0].id).first()
            print(f"   Found user: {user.email if user else 'None'}")
        
        # Test 3: Complex queries
        print("\n3. Testing complex queries...")
        entries = db.query(JournalEntry).filter(JournalEntry.user_id == 1).all()
        print(f"   Found {len(entries)} journal entries for user 1")
        
        # Test 4: Multiple operations
        print("\n4. Testing multiple operations...")
        for i in range(5):
            db.query(User).first()
            time.sleep(0.01)  # Small delay to simulate real usage
        
        # Test 5: Performance statistics
        print("\n5. Checking performance statistics...")
        stats = get_query_performance_stats()
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Total time: {stats['total_time']:.4f}s")
        print(f"   Average time: {stats['average_time']:.4f}s")
        print(f"   Slow queries: {stats['slow_queries_count']}")
        
        if stats['slow_queries']:
            print("\n   Recent slow queries:")
            for query in stats['slow_queries'][-3:]:  # Last 3 slow queries
                print(f"     {query['duration']:.4f}s - {query['sql'][:50]}...")
        
        print("\n✅ Query logging test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        raise
    finally:
        db.close()

def check_log_files():
    """Check if log files are being created"""
    
    print("\nChecking log files...")
    
    import os
    
    log_files = [
        "logs/database_queries.log",
        "logs/slow_queries.log", 
        "logs/error_queries.log",
        "logs/performance_metrics.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"   ✅ {log_file} exists ({size} bytes)")
        else:
            print(f"   ❌ {log_file} not found")

if __name__ == "__main__":
    test_query_logging()
    check_log_files()