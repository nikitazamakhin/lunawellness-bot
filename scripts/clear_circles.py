"""Clear all video circles from database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def main():
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM circles")
        await db.commit()
        print("✅ Все кружки удалены из базы данных")
        print("\nТеперь отправь кружки заново в правильном порядке через /setcircle")


if __name__ == "__main__":
    asyncio.run(main())
