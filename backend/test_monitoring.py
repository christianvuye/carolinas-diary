#!/usr/bin/env python3
"""
Test script for performance monitoring middleware
"""

import time
import requests
import json

def test_performance_monitoring():
    """Test the performance monitoring middleware"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Performance Monitoring Middleware")
    print("=" * 50)
    
    # Test 1: Fast request (should be logged as INFO)
    print("\n1. Testing fast request...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Fast request completed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server with: uvicorn main:app --reload")
        return
    
    # Test 2: Slow request simulation (should be logged as WARNING)
    print("\n2. Testing slow request simulation...")
    try:
        # This endpoint might be slow due to database operations
        response = requests.get(f"{base_url}/gratitude-questions")
        print(f"✅ Slow request test completed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing slow request: {e}")
    
    # Test 3: Very slow request simulation (should be logged as ERROR/CRITICAL)
    print("\n3. Testing very slow request simulation...")
    try:
        # Multiple requests to potentially trigger slow performance
        for i in range(5):
            response = requests.get(f"{base_url}/emotions")
            print(f"   Request {i+1}: {response.status_code}")
        print("✅ Very slow request test completed")
    except Exception as e:
        print(f"❌ Error testing very slow request: {e}")
    
    # Test 4: Error request (should be logged as ERROR)
    print("\n4. Testing error request...")
    try:
        response = requests.get(f"{base_url}/nonexistent-endpoint")
        print(f"✅ Error request test completed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing error request: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Check the server logs to see performance monitoring in action!")
    print("   Look for log messages with different levels:")
    print("   - INFO: Normal requests")
    print("   - WARNING: Slow requests (>0.5s)")
    print("   - ERROR: Very slow requests (>2.0s)")
    print("   - CRITICAL: Performance alerts")

if __name__ == "__main__":
    test_performance_monitoring()