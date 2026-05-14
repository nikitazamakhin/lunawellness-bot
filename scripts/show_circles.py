"""Show current video circles order."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database import init_db
from bot.i18n import TRANSLATIONS
import aiosqlite

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def main():
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT step, file_id FROM circles ORDER BY step")
        rows = await cursor.fetchall()

    print("=" * 80)
    print("ТЕКУЩИЙ ПОРЯДОК КРУЖКОВ В БАЗЕ ДАННЫХ")
    print("=" * 80)

    for step, file_id in rows:
        # Get text preview
        text_key = f"funnel_step_{step}"
        text = TRANSLATIONS["ru"].get(text_key, "")

        # Extract title from text
        if "<b>" in text:
            title = text.split("<b>")[1].split("</b>")[0]
        else:
            title = text[:50] + "..."

        print(f"\nШаг {step}: {title}")
        print(f"  File ID: {file_id[:50]}...")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
