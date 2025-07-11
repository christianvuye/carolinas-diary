#!/usr/bin/env python3
"""
Setup script for PostgreSQL database with analytics tracking.
This script helps set up the database and run initial migrations.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_docker():
    """Check if Docker is available"""
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Docker is not available. Please install Docker first.")
        return False
    print("✅ Docker is available")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Docker Compose is not available. Please install Docker Compose first.")
        return False
    print("✅ Docker Compose is available")
    return True

def start_postgres():
    """Start PostgreSQL using Docker Compose"""
    print("🚀 Starting PostgreSQL database...")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Start the services
    result = run_command("docker-compose up -d postgres", "Starting PostgreSQL container")
    if result is None:
        return False
    
    # Wait for PostgreSQL to be ready
    print("⏳ Waiting for PostgreSQL to be ready...")
    import time
    time.sleep(10)
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    result = run_command("pip install -r requirements.txt", "Installing dependencies")
    return result is not None

def setup_alembic():
    """Set up Alembic for database migrations"""
    print("🗄️ Setting up Alembic...")
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Initialize Alembic if not already initialized
    if not Path("alembic.ini").exists():
        result = run_command("alembic init alembic", "Initializing Alembic")
        if result is None:
            return False
    
    return True

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Create initial migration
    result = run_command("alembic revision --autogenerate -m 'Initial migration with analytics tables'", 
                        "Creating initial migration")
    if result is None:
        return False
    
    # Run migrations
    result = run_command("alembic upgrade head", "Running migrations")
    return result is not None

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_example = Path(__file__).parent / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ .env file created from .env.example")
        else:
            print("⚠️ .env.example not found, please create .env file manually")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🎯 Setting up PostgreSQL with analytics tracking for Carolina's Diary")
    print("=" * 60)
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    if not check_docker_compose():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Start PostgreSQL
    if not start_postgres():
        print("❌ Failed to start PostgreSQL")
        sys.exit(1)
    
    # Setup Alembic
    if not setup_alembic():
        print("❌ Failed to setup Alembic")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📊 Your PostgreSQL database is now ready with analytics tracking!")
    print("\n📋 Next steps:")
    print("1. Update your .env file with the correct DATABASE_URL:")
    print("   DATABASE_URL=postgresql://diary_user:diary_password@localhost:5432/carolinas_diary")
    print("2. Start your FastAPI application")
    print("3. Access pgAdmin at http://localhost:8080 (admin@carolinasdiary.com / admin_password)")
    print("4. Connect to PostgreSQL using:")
    print("   - Host: localhost")
    print("   - Port: 5432")
    print("   - Database: carolinas_diary")
    print("   - Username: diary_user")
    print("   - Password: diary_password")
    print("\n📈 Analytics tracking includes:")
    print("- Daily/Weekly/Monthly Active Users")
    print("- Session duration and frequency")
    print("- Feature usage patterns")
    print("- User retention curves")
    print("- Entry completion rates")

if __name__ == "__main__":
    main()