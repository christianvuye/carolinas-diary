#!/usr/bin/env python3
"""
Database Monitoring Demo
Demonstrates the database query logging and monitoring features
"""

import time
import requests
import json
from datetime import datetime

def demo_api_monitoring():
    """Demonstrate the API monitoring endpoint"""
    
    print("🌐 API Monitoring Demo")
    print("=" * 40)
    
    try:
        # Try to connect to the API
        response = requests.get("http://localhost:8000/admin/database-performance", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Successfully retrieved performance statistics:")
            print(f"   Total Queries: {stats.get('total_queries', 0)}")
            print(f"   Total Time: {stats.get('total_time', 0):.4f}s")
            print(f"   Average Time: {stats.get('average_time', 0):.4f}s")
            print(f"   Slow Queries: {stats.get('slow_queries_count', 0)}")
            
            if stats.get('slow_queries'):
                print("\n   Recent Slow Queries:")
                for query in stats['slow_queries'][-3:]:
                    print(f"     {query['duration']:.4f}s - {query['sql'][:50]}...")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error accessing API: {e}")

def demo_log_analysis():
    """Demonstrate log analysis capabilities"""
    
    print("\n📊 Log Analysis Demo")
    print("=" * 40)
    
    try:
        # Import the analyzer
        from db_monitor import DatabaseQueryAnalyzer
        
        analyzer = DatabaseQueryAnalyzer()
        
        # Generate a quick report
        print("Generating performance report for the last hour...")
        report = analyzer.generate_report(hours_back=1)
        
        if "Error:" in report:
            print("❌ No query data found in the last hour")
            print("   Try running some database operations first")
        else:
            print("✅ Performance report generated successfully")
            print("\nReport preview:")
            lines = report.split('\n')[:20]  # Show first 20 lines
            for line in lines:
                print(f"   {line}")
            
            if len(report.split('\n')) > 20:
                print("   ... (truncated)")
        
    except ImportError:
        print("❌ Could not import DatabaseQueryAnalyzer")
    except Exception as e:
        print(f"❌ Error during log analysis: {e}")

def demo_real_time_monitoring():
    """Demonstrate real-time monitoring capabilities"""
    
    print("\n⏱️  Real-time Monitoring Demo")
    print("=" * 40)
    
    import os
    
    # Check if log files exist
    log_files = [
        "logs/database_queries.log",
        "logs/slow_queries.log",
        "logs/error_queries.log"
    ]
    
    print("Checking log files:")
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"   ✅ {log_file} ({size} bytes)")
        else:
            print(f"   ❌ {log_file} not found")
    
    # Show recent log entries
    print("\nRecent database queries (last 5 lines):")
    if os.path.exists("logs/database_queries.log"):
        try:
            with open("logs/database_queries.log", "r") as f:
                lines = f.readlines()
                recent_lines = lines[-5:] if len(lines) >= 5 else lines
                for line in recent_lines:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   Error reading log file: {e}")
    else:
        print("   No query log file found")

def demo_command_line_tools():
    """Demonstrate command-line tool usage"""
    
    print("\n🛠️  Command-line Tools Demo")
    print("=" * 40)
    
    print("Available commands:")
    print("   python db_monitor.py                    # Generate 24-hour report")
    print("   python db_monitor.py --hours 48        # Generate 48-hour report")
    print("   python db_monitor.py --json            # Export as JSON")
    print("   python db_monitor.py --slow-only 0.2   # Show queries > 200ms")
    print("   python db_monitor.py --output report.txt # Save to file")
    
    print("\nExample usage:")
    print("   # Monitor slow queries in real-time:")
    print("   tail -f logs/slow_queries.log")
    print("")
    print("   # Check performance statistics:")
    print("   curl http://localhost:8000/admin/database-performance")
    print("")
    print("   # Generate daily report:")
    print("   python db_monitor.py --hours 24 --output daily_report.txt")

def main():
    """Run all demos"""
    
    print("🚀 Database Query Performance Monitoring Demo")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run all demos
    demo_api_monitoring()
    demo_log_analysis()
    demo_real_time_monitoring()
    demo_command_line_tools()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("\nNext steps:")
    print("1. Start your application: python main.py")
    print("2. Generate some database activity")
    print("3. Monitor logs: tail -f logs/database_queries.log")
    print("4. Generate reports: python db_monitor.py")
    print("5. Check API: curl http://localhost:8000/admin/database-performance")

if __name__ == "__main__":
    main()