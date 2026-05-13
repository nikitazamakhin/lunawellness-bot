"""LUNA Wellness Bot — Entry Point."""

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.database import init_db
from bot.handlers import start, menu, booking, admin
from bot.services.scheduler import resume_funnels

# Log to file for launchd (no stdout/stderr capture issues)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("Database initialized")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)

    # Resume incomplete funnels from before restart
    await resume_funnels(bot)
    logger.info("Incomplete funnels resumed")

    logger.info("Starting LUNA Wellness Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
