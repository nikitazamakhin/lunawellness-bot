"""Complete bot connection diagnostics."""
import asyncio
from aiogram import Bot
from bot.config import settings


async def main():
    bot = Bot(token=settings.bot_token)
    try:
        print("🔍 ДИАГНОСТИКА БОТА\n")

        # 1. Get bot info
        me = await bot.get_me()
        print(f"✅ Бот: @{me.username} (ID: {me.id})")
        print(f"   Имя: {me.first_name}\n")

        # 2. Check webhook status
        webhook = await bot.get_webhook_info()
        print("📡 WEBHOOK СТАТУС:")
        print(f"   URL: {webhook.url or '❌ Не установлен (polling mode)'}")
        print(f"   Pending updates: {webhook.pending_update_count}")
        print(f"   Last error: {webhook.last_error_message or 'Нет'}")
        if webhook.last_error_date:
            from datetime import datetime
            error_time = datetime.fromtimestamp(webhook.last_error_date)
            print(f"   Last error time: {error_time}")
        print(f"   Max connections: {webhook.max_connections or 'N/A'}")
        print(f"   IP address: {webhook.ip_address or 'N/A'}")

        if webhook.url:
            print("\n⚠️  ОБНАРУЖЕН WEBHOOK! Это может быть источник конфликта.")
            print("   Для polling режима нужно удалить webhook:")
            print("   python3 delete_webhook.py\n")

        # 3. Get updates to test connection
        print("\n🔄 ТЕСТ ПОДКЛЮЧЕНИЯ:")
        try:
            updates = await bot.get_updates(limit=1, timeout=5)
            print(f"   ✅ Успешно получены updates (count: {len(updates)})")
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            if "Conflict" in str(e):
                print("\n🚨 КОНФЛИКТ ОБНАРУЖЕН!")
                print("   Это означает, что кто-то другой ПРЯМО СЕЙЧАС подключен к боту.")
                print("\n   Возможные причины:")
                print("   1. Webhook на сервере (проверьте выше)")
                print("   2. Бот запущен на другом компьютере")
                print("   3. Бот запущен в облаке (Heroku, DigitalOcean, AWS и т.д.)")
                print("   4. ⚠️  Несанкционированный доступ (если вы точно не запускали)")
                print("\n   РЕШЕНИЕ:")
                print("   - Если у вас есть webhook/сервер - отключите его")
                print("   - Если токен скомпрометирован - СМЕНИТЕ ТОКЕН через @BotFather")

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
