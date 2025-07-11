import os
import sqlite3
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from models import User, JournalEntry, GratitudeQuestion, EmotionQuestion, Quote


class DatabaseMonitor:
    def __init__(self, db_path: str = "./carolinas_diary.db"):
        self.db_path = db_path
    
    def get_database_size(self) -> Dict:
        """Get the total size of the database file"""
        try:
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                size_mb = size_bytes / (1024 * 1024)
                return {
                    "size_bytes": size_bytes,
                    "size_mb": round(size_mb, 2),
                    "size_kb": round(size_bytes / 1024, 2),
                    "human_readable": f"{size_mb:.2f} MB"
                }
            else:
                return {
                    "size_bytes": 0,
                    "size_mb": 0,
                    "size_kb": 0,
                    "human_readable": "0 MB"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_sizes(self, db: Session) -> List[Dict]:
        """Get the size of each table in the database"""
        try:
            # Connect to SQLite database for size information
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tables = ['users', 'journal_entries', 'gratitude_questions', 'emotion_questions', 'quotes']
            table_sizes = []
            
            for table in tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                # Get table size in pages (SQLite specific)
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # Estimate table size (rough calculation)
                estimated_size_bytes = row_count * 1024  # Rough estimate
                
                table_sizes.append({
                    "table_name": table,
                    "row_count": row_count,
                    "estimated_size_bytes": estimated_size_bytes,
                    "estimated_size_kb": round(estimated_size_bytes / 1024, 2),
                    "estimated_size_mb": round(estimated_size_bytes / (1024 * 1024), 2)
                })
            
            conn.close()
            return table_sizes
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_detailed_table_info(self, db: Session) -> List[Dict]:
        """Get detailed information about each table"""
        try:
            tables = [
                (User, "users"),
                (JournalEntry, "journal_entries"),
                (GratitudeQuestion, "gratitude_questions"),
                (EmotionQuestion, "emotion_questions"),
                (Quote, "quotes")
            ]
            
            detailed_info = []
            
            for model, table_name in tables:
                # Get row count
                row_count = db.query(model).count()
                
                # Get oldest and newest records
                oldest_record = db.query(model).order_by(model.id).first()
                newest_record = db.query(model).order_by(model.id.desc()).first()
                
                # Get size distribution if applicable
                size_info = {}
                if hasattr(model, 'created_at'):
                    # Get records by month for the last 6 months
                    six_months_ago = datetime.now() - timedelta(days=180)
                    recent_count = db.query(model).filter(
                        model.created_at >= six_months_ago
                    ).count()
                    size_info = {
                        "recent_records": recent_count,
                        "oldest_record_date": oldest_record.created_at if oldest_record else None,
                        "newest_record_date": newest_record.created_at if newest_record else None
                    }
                
                detailed_info.append({
                    "table_name": table_name,
                    "row_count": row_count,
                    "size_info": size_info
                })
            
            return detailed_info
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_system_metrics(self) -> Dict:
        """Get system-level metrics"""
        try:
            # Get disk usage for the database directory
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            disk_usage = psutil.disk_usage(db_dir)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            
            return {
                "disk": {
                    "total_gb": round(disk_usage.total / (1024**3), 2),
                    "used_gb": round(disk_usage.used / (1024**3), 2),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "percent_used": disk_usage.percent
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent
                },
                "cpu_percent": psutil.cpu_percent(interval=1)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_growth_metrics(self, db: Session) -> Dict:
        """Get database growth metrics over time"""
        try:
            # Get journal entries growth over time
            entries_by_month = db.query(
                func.strftime('%Y-%m', JournalEntry.created_at).label('month'),
                func.count(JournalEntry.id).label('count')
            ).group_by('month').order_by('month').all()
            
            # Get user growth over time
            users_by_month = db.query(
                func.strftime('%Y-%m', User.created_at).label('month'),
                func.count(User.id).label('count')
            ).group_by('month').order_by('month').all()
            
            return {
                "journal_entries_growth": [
                    {"month": month, "count": count} 
                    for month, count in entries_by_month
                ],
                "users_growth": [
                    {"month": month, "count": count} 
                    for month, count in users_by_month
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_database_health(self, db: Session) -> Dict:
        """Get overall database health metrics"""
        try:
            total_size = self.get_database_size()
            table_sizes = self.get_table_sizes(db)
            system_metrics = self.get_system_metrics()
            
            # Calculate total rows across all tables
            total_rows = sum(table.get('row_count', 0) for table in table_sizes)
            
            # Determine health status
            health_status = "healthy"
            warnings = []
            
            # Check database size
            if total_size.get('size_mb', 0) > 100:  # 100MB threshold
                health_status = "warning"
                warnings.append("Database size exceeds 100MB")
            
            # Check disk space
            if system_metrics.get('disk', {}).get('percent_used', 0) > 90:
                health_status = "critical"
                warnings.append("Disk usage exceeds 90%")
            
            # Check memory usage
            if system_metrics.get('memory', {}).get('percent_used', 0) > 90:
                health_status = "warning"
                warnings.append("Memory usage exceeds 90%")
            
            return {
                "status": health_status,
                "warnings": warnings,
                "total_rows": total_rows,
                "database_size": total_size,
                "system_metrics": system_metrics
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_performance_metrics(self, db: Session) -> Dict:
        """Get database performance metrics"""
        try:
            # Get average entries per user
            total_users = db.query(User).count()
            total_entries = db.query(JournalEntry).count()
            
            avg_entries_per_user = total_entries / total_users if total_users > 0 else 0
            
            # Get most active users (top 5)
            active_users = db.query(
                User.id,
                User.name,
                func.count(JournalEntry.id).label('entry_count')
            ).join(JournalEntry).group_by(User.id).order_by(
                func.count(JournalEntry.id).desc()
            ).limit(5).all()
            
            return {
                "total_users": total_users,
                "total_entries": total_entries,
                "avg_entries_per_user": round(avg_entries_per_user, 2),
                "most_active_users": [
                    {
                        "user_id": user.id,
                        "name": user.name,
                        "entry_count": entry_count
                    }
                    for user, entry_count in active_users
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}