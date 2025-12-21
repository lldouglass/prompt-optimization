"""
Migration script to add token tracking columns to the organizations table.

Run with: cd backend && uv run python scripts/add_token_tracking_columns.py
"""

import sqlite3
from pathlib import Path


def migrate():
    # Find the database file
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
        print("No database found. Migration not needed (will be created on first run).")
        return

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(organizations)")
    columns = {row[1] for row in cursor.fetchall()}

    # Add tokens_used_this_month if not exists
    if "tokens_used_this_month" not in columns:
        print("Adding column: tokens_used_this_month")
        cursor.execute(
            "ALTER TABLE organizations ADD COLUMN tokens_used_this_month INTEGER DEFAULT 0"
        )
    else:
        print("Column already exists: tokens_used_this_month")

    # Add estimated_cost_cents if not exists
    if "estimated_cost_cents" not in columns:
        print("Adding column: estimated_cost_cents")
        cursor.execute(
            "ALTER TABLE organizations ADD COLUMN estimated_cost_cents INTEGER DEFAULT 0"
        )
    else:
        print("Column already exists: estimated_cost_cents")

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    migrate()
