"""Reset user's funnel progress."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def reset_user(telegram_id: int):
    """Reset user's funnel_step to 0 and language to default."""
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        # Check if user exists
        cursor = await db.execute("SELECT first_name FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()

        if not row:
            print(f"❌ Пользователь {telegram_id} не найден в базе")
            return

        # Reset to new user state
        await db.execute(
            "UPDATE users SET funnel_step = 0, language = 'ru' WHERE telegram_id = ?",
            (telegram_id,)
        )
        await db.commit()

        print(f"✅ Пользователь {row[0]} ({telegram_id}) сброшен")
        print(f"   - funnel_step: 0")
        print(f"   - language: ru (по умолчанию)")
        print(f"\nТеперь при /start покажется выбор языка!")


async def main():
    if len(sys.argv) != 2:
        print("Использование: python3 reset_user.py <telegram_id>")
        print("Пример: python3 reset_user.py 5372683522")
        return

    telegram_id = int(sys.argv[1])
    await reset_user(telegram_id)


if __name__ == "__main__":
    asyncio.run(main())
