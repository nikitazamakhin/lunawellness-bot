"""Swap two video circles in database."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def swap_circles(step1: int, step2: int):
    """Swap circles between two steps."""
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        # Get both circles
        cursor1 = await db.execute("SELECT file_id FROM circles WHERE step = ?", (step1,))
        row1 = await cursor1.fetchone()

        cursor2 = await db.execute("SELECT file_id FROM circles WHERE step = ?", (step2,))
        row2 = await cursor2.fetchone()

        if not row1:
            print(f"❌ Кружок для шага {step1} не найден")
            return

        if not row2:
            print(f"❌ Кружок для шага {step2} не найден")
            return

        file_id1 = row1[0]
        file_id2 = row2[0]

        # Swap them
        await db.execute("UPDATE circles SET file_id = ? WHERE step = ?", (file_id2, step1))
        await db.execute("UPDATE circles SET file_id = ? WHERE step = ?", (file_id1, step2))
        await db.commit()

        print(f"✅ Поменяли местами кружки шага {step1} и шага {step2}")


async def main():
    if len(sys.argv) != 3:
        print("Использование: python3 swap_circles.py <шаг1> <шаг2>")
        print("Пример: python3 swap_circles.py 4 5")
        return

    step1 = int(sys.argv[1])
    step2 = int(sys.argv[2])

    await swap_circles(step1, step2)


if __name__ == "__main__":
    asyncio.run(main())
