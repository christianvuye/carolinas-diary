#!/usr/bin/env python3
"""
Database migration script for Carolina's Diary
Converts single-user database to multi-user with Firebase authentication
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def backup_database(db_path):
    """Create a backup of the current database"""
    backup_path = f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_full_path = db_path.parent / backup_path

    # Copy the database file
    shutil.copy2(db_path, backup_full_path)
    print(f"Database backed up to: {backup_full_path}")
    return backup_full_path


def check_migration_needed(conn):
    """Check if migration is needed"""
    cursor = conn.cursor()

    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_table_exists = cursor.fetchone() is not None

    # Check if journal_entries has user_id column
    cursor.execute("PRAGMA table_info(journal_entries)")
    columns = [column[1] for column in cursor.fetchall()]
    has_user_id = "user_id" in columns

    return not (users_table_exists and has_user_id)


def migrate_database(db_path):
    """Main migration function"""
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    # Create backup
    backup_path = backup_database(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if migration is needed
        if not check_migration_needed(conn):
            print("Database is already migrated!")
            return True

        print("Starting database migration...")

        # Create users table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                firebase_uid VARCHAR NOT NULL UNIQUE,
                email VARCHAR NOT NULL UNIQUE,
                name VARCHAR,
                picture VARCHAR,
                email_verified BOOLEAN,
                preferences JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for users table
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_firebase_uid ON users (firebase_uid)"
        )

        # Create default user for existing data
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (firebase_uid, email, name, email_verified, preferences)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                "default_user",
                "default@carolinasdiary.com",
                "Default User",
                True,
                json.dumps(
                    {"theme": "light", "notifications": True, "timezone": "UTC"}
                ),
            ),
        )

        # Get the default user ID
        cursor.execute("SELECT id FROM users WHERE firebase_uid = ?", ("default_user",))
        default_user_id = cursor.fetchone()[0]

        # Check if journal_entries table needs migration
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in columns:
            print("Migrating journal_entries table...")

            # Create new journal_entries table with user_id
            cursor.execute(
                """
                CREATE TABLE journal_entries_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    date DATE,
                    gratitude_answers JSON,
                    emotion VARCHAR,
                    emotion_answers JSON,
                    custom_text TEXT,
                    visual_settings JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Copy data from old table, assigning to default user
            cursor.execute(
                """
                INSERT INTO journal_entries_new 
                (id, user_id, date, gratitude_answers, emotion, emotion_answers, custom_text, visual_settings, created_at, updated_at)
                SELECT id, ?, date, gratitude_answers, emotion, emotion_answers, custom_text, visual_settings, created_at, updated_at
                FROM journal_entries
            """,
                (default_user_id,),
            )

            # Drop old table and rename new one
            cursor.execute("DROP TABLE journal_entries")
            cursor.execute("ALTER TABLE journal_entries_new RENAME TO journal_entries")

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON journal_entries(user_id)"
            )

            print("Journal entries table migrated successfully!")

        # Commit the changes
        conn.commit()
        print("Database migration completed successfully!")

        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        entry_count = cursor.fetchone()[0]

        print(
            f"Migration verification: {user_count} users, {entry_count} journal entries"
        )

        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        print(f"Restoring from backup: {backup_path}")

        shutil.copy2(backup_path, db_path)

        return False

    finally:
        conn.close()


def main():
    """Main function"""
    db_path = Path(__file__).parent / "carolinas_diary.db"
    success = migrate_database(db_path)

    if success:
        print("\n✅ Database migration completed successfully!")
    else:
        print("\n❌ Database migration failed!")

    return success


if __name__ == "__main__":
    main()
