"""
Database Monitoring Configuration
Settings and thresholds for database monitoring
"""

# Database size thresholds (in MB)
DATABASE_SIZE_THRESHOLDS = {
    "warning": 50,    # Warning when database exceeds 50MB
    "critical": 100,  # Critical when database exceeds 100MB
    "max": 500        # Maximum recommended size
}

# Disk usage thresholds (in percentage)
DISK_USAGE_THRESHOLDS = {
    "warning": 80,    # Warning when disk usage exceeds 80%
    "critical": 90    # Critical when disk usage exceeds 90%
}

# Memory usage thresholds (in percentage)
MEMORY_USAGE_THRESHOLDS = {
    "warning": 80,    # Warning when memory usage exceeds 80%
    "critical": 90    # Critical when memory usage exceeds 90%
}

# Table row count thresholds
TABLE_ROW_THRESHOLDS = {
    "users": {
        "warning": 1000,
        "critical": 5000
    },
    "journal_entries": {
        "warning": 10000,
        "critical": 50000
    },
    "gratitude_questions": {
        "warning": 100,
        "critical": 500
    },
    "emotion_questions": {
        "warning": 500,
        "critical": 2000
    },
    "quotes": {
        "warning": 1000,
        "critical": 5000
    }
}

# Monitoring intervals (in seconds)
MONITORING_INTERVALS = {
    "database_size": 300,      # Check every 5 minutes
    "system_metrics": 60,      # Check every minute
    "health_check": 300,       # Health check every 5 minutes
    "performance_metrics": 600  # Performance metrics every 10 minutes
}

# Alert settings
ALERT_SETTINGS = {
    "enable_email_alerts": False,
    "enable_log_alerts": True,
    "log_file": "database_monitoring.log",
    "alert_levels": ["critical", "warning"]
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "max_query_time": 5.0,     # Maximum query time in seconds
    "max_connections": 100,     # Maximum database connections
    "min_free_disk_gb": 10,    # Minimum free disk space in GB
    "min_free_memory_gb": 2    # Minimum free memory in GB
}

# Growth monitoring settings
GROWTH_MONITORING = {
    "track_monthly_growth": True,
    "growth_warning_percentage": 50,  # Warning if growth exceeds 50% in a month
    "max_monthly_growth": 200,        # Maximum 200% growth per month
    "retention_days": 365             # Keep growth data for 1 year
}

# Backup settings
BACKUP_SETTINGS = {
    "enable_auto_backup": True,
    "backup_interval_hours": 24,
    "backup_retention_days": 7,
    "backup_directory": "./backups"
}