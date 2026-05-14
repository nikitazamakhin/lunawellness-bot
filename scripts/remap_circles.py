"""Remap circles to correct order."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def remap_circles(mapping: dict):
    """
    Remap circles according to new order.

    mapping = {new_step: old_step}
    Example: {1: 3, 2: 1, 3: 2} means:
      - what's now on step 3 should be on step 1
      - what's now on step 1 should be on step 2
      - what's now on step 2 should be on step 3
    """
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        # Get all current circles
        cursor = await db.execute("SELECT step, file_id FROM circles ORDER BY step")
        current = {row[0]: row[1] for row in await cursor.fetchall()}

        # Build new mapping
        new_circles = {}
        for new_step, old_step in mapping.items():
            if old_step not in current:
                print(f"❌ Ошибка: кружок на шаге {old_step} не найден")
                return
            new_circles[new_step] = current[old_step]

        # Clear and insert new order
        await db.execute("DELETE FROM circles")
        for step, file_id in new_circles.items():
            await db.execute("INSERT INTO circles (step, file_id) VALUES (?, ?)", (step, file_id))

        await db.commit()

        print("✅ Кружки переназначены:")
        for new_step, old_step in sorted(mapping.items()):
            print(f"   Шаг {new_step}: взят кружок со старого шага {old_step}")


async def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║           ПЕРЕНАЗНАЧЕНИЕ КРУЖКОВ                          ║
╚═══════════════════════════════════════════════════════════╝

Посмотри на кружки которые были отправлены в Telegram.
Сейчас они идут как "Шаг 1", "Шаг 2" ... "Шаг 7"

Введи правильный порядок в формате:
  новый_шаг:старый_шаг

Пример:
  1:3  (кружок который сейчас на шаге 3 должен быть на шаге 1)
  2:1  (кружок который сейчас на шаге 1 должен быть на шаге 2)
  3:5  (кружок со старого шага 5 должен быть на шаге 3)
  и так далее...

Вводи по одному на строке. Когда закончишь — введи "готово"
""")

    mapping = {}

    while True:
        line = input(">>> ").strip()

        if line.lower() in ["готово", "done", "q"]:
            break

        if ":" not in line:
            print("❌ Неверный формат. Используй формат: новый_шаг:старый_шаг")
            continue

        try:
            new_step, old_step = line.split(":")
            new_step = int(new_step.strip())
            old_step = int(old_step.strip())

            if not (1 <= new_step <= 7 and 1 <= old_step <= 7):
                print("❌ Шаги должны быть от 1 до 7")
                continue

            mapping[new_step] = old_step
            print(f"   ✓ Шаг {new_step} ← кружок со старого шага {old_step}")

        except ValueError:
            print("❌ Неверный формат. Используй числа.")
            continue

    if not mapping:
        print("❌ Не введено ни одного маппинга")
        return

    # Check that all steps 1-7 are covered
    if set(mapping.keys()) != set(range(1, 8)):
        print(f"❌ Нужно указать все шаги 1-7. Указано: {sorted(mapping.keys())}")
        return

    print(f"\n📝 Будет применён маппинг:")
    for new_step, old_step in sorted(mapping.items()):
        print(f"   Шаг {new_step} ← кружок со шага {old_step}")

    confirm = input("\nПрименить? (да/нет): ").strip().lower()

    if confirm in ["да", "yes", "y"]:
        await remap_circles(mapping)
    else:
        print("❌ Отменено")


if __name__ == "__main__":
    asyncio.run(main())
