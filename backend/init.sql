-- Initialize the database with basic setup
-- This script runs when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance on analytics queries
-- (These will be created by SQLAlchemy, but we can add custom ones here if needed)

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE carolinas_diary TO diary_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO diary_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO diary_user;