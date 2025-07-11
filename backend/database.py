from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from datetime import datetime
from logging_config import setup_database_logging, get_performance_logger

# Setup logging
db_logger = setup_database_logging()
perf_logger = get_performance_logger()

# SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./carolinas_diary.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQL Query Performance Monitoring
class QueryPerformanceMonitor:
    def __init__(self):
        self.query_count = 0
        self.total_time = 0
        self.slow_queries = []  # Queries taking > 100ms
        self.query_times = []
    
    def log_query(self, sql, params, duration):
        self.query_count += 1
        self.total_time += duration
        self.query_times.append(duration)
        
        # Log all queries
        db_logger.info(f"Query executed in {duration:.4f}s: {sql[:200]}...")
        
        # Track slow queries (> 100ms)
        if duration > 0.1:
            self.slow_queries.append({
                'sql': sql,
                'params': params,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            db_logger.warning(f"SLOW QUERY ({duration:.4f}s): {sql}")
        
        # Log performance metrics every 10 queries
        if self.query_count % 10 == 0:
            avg_time = self.total_time / self.query_count
            perf_logger.info(f"Performance Summary - Queries: {self.query_count}, "
                           f"Total Time: {self.total_time:.4f}s, "
                           f"Avg Time: {avg_time:.4f}s, "
                           f"Slow Queries: {len(self.slow_queries)}")

# Global performance monitor
performance_monitor = QueryPerformanceMonitor()

# SQLAlchemy event listeners for query logging
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    
    # Log the query performance
    performance_monitor.log_query(statement, parameters, total)
    
    # Additional detailed logging for very slow queries (> 500ms)
    if total > 0.5:
        db_logger.error(f"VERY SLOW QUERY DETECTED ({total:.4f}s):")
        db_logger.error(f"SQL: {statement}")
        db_logger.error(f"Parameters: {parameters}")
        db_logger.error(f"Connection: {conn}")

# Function to get performance statistics
def get_query_performance_stats():
    """Get current query performance statistics"""
    if performance_monitor.query_count == 0:
        return {
            "total_queries": 0,
            "total_time": 0,
            "average_time": 0,
            "slow_queries_count": 0,
            "slow_queries": []
        }
    
    avg_time = performance_monitor.total_time / performance_monitor.query_count
    return {
        "total_queries": performance_monitor.query_count,
        "total_time": performance_monitor.total_time,
        "average_time": avg_time,
        "slow_queries_count": len(performance_monitor.slow_queries),
        "slow_queries": performance_monitor.slow_queries[-10:]  # Last 10 slow queries
    }
