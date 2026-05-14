"""Delete webhook to allow polling mode."""
import asyncio
from aiogram import Bot
from bot.config import settings


async def main():
    bot = Bot(token=settings.bot_token)
    try:
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted successfully")

        # Get current webhook info
        info = await bot.get_webhook_info()
        print(f"📍 Current webhook URL: {info.url or 'None (polling mode)'}")

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
