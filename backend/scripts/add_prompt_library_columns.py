"""
Migration script to add Prompt Library columns to the prompt_optimizations table.

For local SQLite:
    cd backend && uv run python scripts/add_prompt_library_columns.py

For production PostgreSQL:
    fly ssh console --app clarynt-api
    cd /app && python scripts/add_prompt_library_columns.py
"""

import asyncio
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def migrate_postgres():
    """Migrate PostgreSQL database (production)."""
    from sqlalchemy import text
    from app.database import engine

    columns_to_add = [
        ("name", "VARCHAR(255)"),
        ("folder", "VARCHAR(100)"),
        ("media_type", "VARCHAR(20)"),
        ("target_model", "VARCHAR(50)"),
        ("negative_prompt", "TEXT"),
        ("parameters", "TEXT"),
        ("tips", "JSONB"),
        ("web_sources", "JSONB"),
        ("aspect_ratio", "VARCHAR(20)"),
    ]

    async with engine.begin() as conn:
        for col_name, col_type in columns_to_add:
            try:
                await conn.execute(text(
                    f"ALTER TABLE prompt_optimizations ADD COLUMN {col_name} {col_type}"
                ))
                print(f"Added column: {col_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate" in error_msg:
                    print(f"Column already exists: {col_name}")
                else:
                    print(f"Error adding {col_name}: {e}")

        # Add indexes
        indexes = [
            ("idx_optimizations_folder", "org_id, folder"),
            ("idx_optimizations_media_type", "org_id, media_type"),
        ]
        for idx_name, idx_cols in indexes:
            try:
                await conn.execute(text(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON prompt_optimizations ({idx_cols})"
                ))
                print(f"Created index: {idx_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"Index already exists: {idx_name}")
                else:
                    print(f"Error creating index {idx_name}: {e}")

    print("PostgreSQL migration complete!")


def migrate_sqlite():
    """Migrate SQLite database (local development)."""
    import sqlite3
    from pathlib import Path

    db_paths = [
        Path("test.db"),
        Path("backend/test.db"),
        Path(__file__).parent.parent / "test.db",
    ]

    db_path = None
    for p in db_paths:
        if p.exists():
            db_path = p
            break

    if not db_path:
        print("No SQLite database found. Migration not needed (will be created on first run).")
        return

    print(f"Migrating SQLite database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(prompt_optimizations)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = [
        ("name", "VARCHAR(255)"),
        ("folder", "VARCHAR(100)"),
        ("media_type", "VARCHAR(20)"),
        ("target_model", "VARCHAR(50)"),
        ("negative_prompt", "TEXT"),
        ("parameters", "TEXT"),
        ("tips", "TEXT"),  # SQLite doesn't have JSONB
        ("web_sources", "TEXT"),
        ("aspect_ratio", "VARCHAR(20)"),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE prompt_optimizations ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column already exists: {col_name}")

    conn.commit()
    conn.close()
    print("SQLite migration complete!")


def main():
    # Check if we're running against PostgreSQL (production) or SQLite (local)
    database_url = os.environ.get("DATABASE_URL", "")

    if "postgresql" in database_url or "asyncpg" in database_url:
        print("Detected PostgreSQL database, running async migration...")
        asyncio.run(migrate_postgres())
    else:
        print("Running SQLite migration for local development...")
        migrate_sqlite()


if __name__ == "__main__":
    main()
