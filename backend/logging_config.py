import logging
import logging.handlers
import os
from datetime import datetime

def setup_database_logging():
    """Setup comprehensive database logging configuration"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create database logger
    db_logger = logging.getLogger('database_queries')
    db_logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if db_logger.handlers:
        return db_logger
    
    # File handler with rotation (10MB max, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/database_queries.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    
    # Slow query file handler
    slow_query_handler = logging.handlers.RotatingFileHandler(
        'logs/slow_queries.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    slow_query_handler.setLevel(logging.WARNING)
    slow_query_handler.setFormatter(logging.Formatter(
        '%(asctime)s - SLOW QUERY - %(message)s'
    ))
    
    # Error query file handler
    error_query_handler = logging.handlers.RotatingFileHandler(
        'logs/error_queries.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_query_handler.setLevel(logging.ERROR)
    error_query_handler.setFormatter(logging.Formatter(
        '%(asctime)s - ERROR QUERY - %(message)s'
    ))
    
    # Add filters for specific handlers
    class SlowQueryFilter(logging.Filter):
        def filter(self, record):
            return 'SLOW QUERY' in record.getMessage()
    
    class ErrorQueryFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.ERROR
    
    slow_query_handler.addFilter(SlowQueryFilter())
    error_query_handler.addFilter(ErrorQueryFilter())
    
    # Add handlers to logger
    db_logger.addHandler(file_handler)
    db_logger.addHandler(console_handler)
    db_logger.addHandler(slow_query_handler)
    db_logger.addHandler(error_query_handler)
    
    return db_logger

def get_performance_logger():
    """Get a dedicated logger for performance metrics"""
    perf_logger = logging.getLogger('database_performance')
    perf_logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if perf_logger.handlers:
        return perf_logger
    
    # Performance metrics file handler
    perf_handler = logging.handlers.RotatingFileHandler(
        'logs/performance_metrics.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    perf_handler.setFormatter(logging.Formatter(
        '%(asctime)s - PERFORMANCE - %(message)s'
    ))
    
    perf_logger.addHandler(perf_handler)
    
    return perf_logger