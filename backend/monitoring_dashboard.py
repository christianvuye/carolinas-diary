#!/usr/bin/env python3
"""
Database Monitoring Dashboard
A simple command-line interface to view database monitoring metrics
"""

import requests
import json
from datetime import datetime
import sys


class MonitoringDashboard:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_data(self, endpoint: str) -> dict:
        """Make a GET request to the monitoring endpoint"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {endpoint}: {e}")
            return {}
    
    def display_database_size(self):
        """Display database size information"""
        print("\n" + "="*50)
        print("DATABASE SIZE")
        print("="*50)
        
        data = self.get_data("/monitoring/database-size")
        if data:
            print(f"Size: {data.get('human_readable', 'N/A')}")
            print(f"Bytes: {data.get('size_bytes', 'N/A'):,}")
            print(f"KB: {data.get('size_kb', 'N/A'):,}")
            print(f"MB: {data.get('size_mb', 'N/A'):,}")
    
    def display_table_sizes(self):
        """Display table size information"""
        print("\n" + "="*50)
        print("TABLE SIZES")
        print("="*50)
        
        data = self.get_data("/monitoring/table-sizes")
        if data:
            for table in data:
                if 'error' not in table:
                    print(f"\n{table['table_name'].upper()}:")
                    print(f"  Rows: {table['row_count']:,}")
                    print(f"  Estimated Size: {table['estimated_size_mb']:.2f} MB")
    
    def display_system_metrics(self):
        """Display system metrics"""
        print("\n" + "="*50)
        print("SYSTEM METRICS")
        print("="*50)
        
        data = self.get_data("/monitoring/system-metrics")
        if data and 'error' not in data:
            disk = data.get('disk', {})
            memory = data.get('memory', {})
            cpu = data.get('cpu_percent', 'N/A')
            
            print(f"CPU Usage: {cpu}%")
            print(f"\nDisk Usage:")
            print(f"  Total: {disk.get('total_gb', 'N/A'):.2f} GB")
            print(f"  Used: {disk.get('used_gb', 'N/A'):.2f} GB")
            print(f"  Free: {disk.get('free_gb', 'N/A'):.2f} GB")
            print(f"  Usage: {disk.get('percent_used', 'N/A'):.1f}%")
            
            print(f"\nMemory Usage:")
            print(f"  Total: {memory.get('total_gb', 'N/A'):.2f} GB")
            print(f"  Available: {memory.get('available_gb', 'N/A'):.2f} GB")
            print(f"  Usage: {memory.get('percent_used', 'N/A'):.1f}%")
    
    def display_database_health(self):
        """Display database health information"""
        print("\n" + "="*50)
        print("DATABASE HEALTH")
        print("="*50)
        
        data = self.get_data("/monitoring/database-health")
        if data and 'error' not in data:
            status = data.get('status', 'unknown')
            warnings = data.get('warnings', [])
            total_rows = data.get('total_rows', 0)
            
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '🚨'
            }
            
            print(f"Status: {status_emoji.get(status, '❓')} {status.upper()}")
            print(f"Total Rows: {total_rows:,}")
            
            if warnings:
                print("\nWarnings:")
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            else:
                print("\n✅ No warnings")
    
    def display_performance_metrics(self):
        """Display performance metrics"""
        print("\n" + "="*50)
        print("PERFORMANCE METRICS")
        print("="*50)
        
        data = self.get_data("/monitoring/performance-metrics")
        if data and 'error' not in data:
            total_users = data.get('total_users', 0)
            total_entries = data.get('total_entries', 0)
            avg_entries = data.get('avg_entries_per_user', 0)
            active_users = data.get('most_active_users', [])
            
            print(f"Total Users: {total_users:,}")
            print(f"Total Entries: {total_entries:,}")
            print(f"Average Entries per User: {avg_entries:.2f}")
            
            if active_users:
                print("\nMost Active Users:")
                for i, user in enumerate(active_users[:5], 1):
                    name = user.get('name', f'User {user.get("user_id", "Unknown")}')
                    entries = user.get('entry_count', 0)
                    print(f"  {i}. {name}: {entries} entries")
    
    def display_growth_metrics(self):
        """Display growth metrics"""
        print("\n" + "="*50)
        print("GROWTH METRICS")
        print("="*50)
        
        data = self.get_data("/monitoring/growth-metrics")
        if data and 'error' not in data:
            entries_growth = data.get('journal_entries_growth', [])
            users_growth = data.get('users_growth', [])
            
            print("Journal Entries Growth (by month):")
            for entry in entries_growth[-6:]:  # Last 6 months
                month = entry.get('month', 'Unknown')
                count = entry.get('count', 0)
                print(f"  {month}: {count} entries")
            
            print("\nUsers Growth (by month):")
            for user in users_growth[-6:]:  # Last 6 months
                month = user.get('month', 'Unknown')
                count = user.get('count', 0)
                print(f"  {month}: {count} users")
    
    def display_comprehensive_report(self):
        """Display a comprehensive monitoring report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE DATABASE MONITORING REPORT")
        print("="*60)
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data = self.get_data("/monitoring/comprehensive-report")
        if data and 'error' not in data:
            # Database Size
            db_size = data.get('database_size', {})
            if db_size:
                print(f"\n📊 Database Size: {db_size.get('human_readable', 'N/A')}")
            
            # Table Sizes
            table_sizes = data.get('table_sizes', [])
            if table_sizes:
                print("\n📋 Table Summary:")
                total_rows = 0
                for table in table_sizes:
                    if 'error' not in table:
                        rows = table.get('row_count', 0)
                        total_rows += rows
                        print(f"  {table['table_name']}: {rows:,} rows")
                print(f"  Total Rows: {total_rows:,}")
            
            # System Health
            health = data.get('database_health', {})
            if health and 'error' not in health:
                status = health.get('status', 'unknown')
                warnings = health.get('warnings', [])
                status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '🚨'}
                print(f"\n🏥 Health Status: {status_emoji.get(status, '❓')} {status.upper()}")
                if warnings:
                    print("  Warnings:")
                    for warning in warnings:
                        print(f"    ⚠️  {warning}")
            
            # Performance
            performance = data.get('performance_metrics', {})
            if performance and 'error' not in performance:
                print(f"\n⚡ Performance:")
                print(f"  Users: {performance.get('total_users', 0):,}")
                print(f"  Entries: {performance.get('total_entries', 0):,}")
                print(f"  Avg Entries/User: {performance.get('avg_entries_per_user', 0):.2f}")
    
    def run_interactive_mode(self):
        """Run the dashboard in interactive mode"""
        while True:
            print("\n" + "="*50)
            print("DATABASE MONITORING DASHBOARD")
            print("="*50)
            print("1. Database Size")
            print("2. Table Sizes")
            print("3. System Metrics")
            print("4. Database Health")
            print("5. Performance Metrics")
            print("6. Growth Metrics")
            print("7. Comprehensive Report")
            print("8. Exit")
            print("="*50)
            
            choice = input("Select an option (1-8): ").strip()
            
            if choice == '1':
                self.display_database_size()
            elif choice == '2':
                self.display_table_sizes()
            elif choice == '3':
                self.display_system_metrics()
            elif choice == '4':
                self.display_database_health()
            elif choice == '5':
                self.display_performance_metrics()
            elif choice == '6':
                self.display_growth_metrics()
            elif choice == '7':
                self.display_comprehensive_report()
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        dashboard = MonitoringDashboard()
        command = sys.argv[1].lower()
        
        if command == 'size':
            dashboard.display_database_size()
        elif command == 'tables':
            dashboard.display_table_sizes()
        elif command == 'system':
            dashboard.display_system_metrics()
        elif command == 'health':
            dashboard.display_database_health()
        elif command == 'performance':
            dashboard.display_performance_metrics()
        elif command == 'growth':
            dashboard.display_growth_metrics()
        elif command == 'report':
            dashboard.display_comprehensive_report()
        else:
            print("Usage: python monitoring_dashboard.py [size|tables|system|health|performance|growth|report]")
            print("Or run without arguments for interactive mode.")
    else:
        # Interactive mode
        dashboard = MonitoringDashboard()
        dashboard.run_interactive_mode()


if __name__ == "__main__":
    main()