"""Show all users in database."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def main():
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT telegram_id, first_name, username, language, funnel_step, booked, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        rows = await cursor.fetchall()

    print("=" * 100)
    print("ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ")
    print("=" * 100)
    print(f"{'ID':<12} {'Имя':<20} {'Username':<20} {'Язык':<6} {'Шаг':<4} {'Записан':<8} {'Создан'}")
    print("-" * 100)

    for row in rows:
        print(
            f"{row['telegram_id']:<12} "
            f"{row['first_name']:<20} "
            f"{row['username'] or '—':<20} "
            f"{row['language']:<6} "
            f"{row['funnel_step']:<4} "
            f"{'Да' if row['booked'] else 'Нет':<8} "
            f"{row['created_at']}"
        )

    print("-" * 100)
    print(f"Всего пользователей: {len(rows)}")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
