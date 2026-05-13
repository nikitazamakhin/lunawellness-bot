"""Migration script to add language column to existing database."""

import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def migrate():
    """Add language column to users table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if column already exists
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "language" not in column_names:
            print("Adding 'language' column to users table...")
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
            await db.commit()
            print("✅ Migration completed: 'language' column added")
        else:
            print("✅ 'language' column already exists, skipping migration")


if __name__ == "__main__":
    asyncio.run(migrate())
