"""Send all circles with their texts to admin for verification."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db, get_all_circles
from bot.i18n import get_funnel_step_text
from bot.config import settings
from aiogram import Bot


async def main():
    """Send all circles with texts to admin."""
    await init_db()

    if len(sys.argv) != 2:
        print("Использование: python3 test_circles.py <telegram_id>")
        print(f"Пример: python3 test_circles.py {settings.admin_id}")
        return

    target_id = int(sys.argv[1])
    bot = Bot(token=settings.bot_token)

    circles = await get_all_circles()

    if not circles:
        print("❌ Нет кружков в базе данных")
        return

    print(f"📤 Отправляю {len(circles)} кружков пользователю {target_id}...")

    for step in sorted(circles.keys()):
        file_id = circles[step]
        text = get_funnel_step_text("ru", step)

        try:
            # Send circle
            await bot.send_video_note(target_id, video_note=file_id)
            await asyncio.sleep(1)

            # Send text
            await bot.send_message(
                target_id,
                f"<b>Шаг {step}:</b>\n\n{text}",
                parse_mode="HTML"
            )
            await asyncio.sleep(2)

            print(f"✅ Шаг {step} отправлен")

        except Exception as e:
            print(f"❌ Ошибка на шаге {step}: {e}")

    await bot.session.close()
    print("\n✅ Готово! Проверь соответствие кружков и текстов в Telegram")


if __name__ == "__main__":
    asyncio.run(main())
