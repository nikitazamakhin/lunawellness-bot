from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import settings
from bot.database import get_stats, get_all_user_ids, get_all_users, save_circle, get_all_circles

router = Router()

STEP_NAMES = {
    1: "Приветствие",
    2: "Тур по студии",
    3: "Направления",
    4: "Атмосфера: Reformer",
    5: "Атмосфера: Aerial/Cycling",
    6: "Атмосфера: SPA",
    7: "Атмосфера: детали",
    8: "Тренеры / доверие",
    9: "Отзывы клиенток",
    10: "Финальный оффер",
}

STEP_TIMINGS = {
    1: "1 мин",
    2: "5 мин",
    3: "15 мин",
    4: "30 мин",
    5: "1 ч",
    6: "2 ч",
    7: "4 ч",
    8: "8 ч",
    9: "16 ч",
    10: "24 ч",
}

MAX_STEPS = 10


@router.message(Command("stats"), F.from_user.id == settings.admin_id)
async def cmd_stats(message: Message):
    stats = await get_stats()
    circles = await get_all_circles()
    funnel_text = "\n".join(
        f"  Шаг {step}: {count}" for step, count in stats["funnel"]
    )
    circles_text = ", ".join(
        f"#{s}" for s in sorted(circles.keys())
    ) if circles else "не загружены"

    text = (
        f"📊 <b>Статистика LUNA Bot</b>\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"✅ Записались: {stats['booked_users']}\n"
        f"🆕 Новых заявок: {stats['new_bookings']}\n\n"
        f"<b>Воронка:</b>\n{funnel_text}\n\n"
        f"<b>Кружочки:</b> {circles_text}\n\n"
        f"<i>Загрузить: отправьте кружочек → ответьте /setcircle N</i>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("setcircle"), F.from_user.id == settings.admin_id)
async def cmd_setcircle(message: Message):
    """Upload a video circle for a funnel step."""
    args = message.text.replace("/setcircle", "").strip()
    if not args or not args.isdigit() or int(args) not in range(1, MAX_STEPS + 1):
        steps_list = "\n".join(
            f"{s} — {STEP_NAMES[s]} ({STEP_TIMINGS[s]})"
            for s in range(1, MAX_STEPS + 1)
        )
        await message.answer(
            "📹 <b>Загрузка кружочков</b>\n\n"
            "Отправьте кружочек в чат, затем "
            "ответьте на него командой:\n"
            "<code>/setcircle 1</code>\n\n"
            f"Номера шагов (1-{MAX_STEPS}):\n"
            f"{steps_list}",
            parse_mode="HTML",
        )
        return

    step = int(args)

    if not message.reply_to_message or not message.reply_to_message.video_note:
        await message.answer(
            f"⚠️ Ответьте командой <code>/setcircle {step}</code> "
            f"на сообщение с кружочком (видео-заметка).",
            parse_mode="HTML",
        )
        return

    file_id = message.reply_to_message.video_note.file_id
    await save_circle(step, file_id)

    await message.answer(
        f"✅ Кружочек #{step} ({STEP_NAMES[step]}) — сохранён!\n\n"
        f"Он будет отправляться новым пользователям на шаге {step} воронки.",
        parse_mode="HTML",
    )


@router.message(Command("circles"), F.from_user.id == settings.admin_id)
async def cmd_circles(message: Message):
    """Show current circle status."""
    circles = await get_all_circles()

    lines = []
    for step in range(1, MAX_STEPS + 1):
        status = "✅" if step in circles else "❌"
        lines.append(f"{status} #{step} — {STEP_NAMES[step]} ({STEP_TIMINGS[step]})")

    text = (
        f"📹 <b>Кружочки воронки ({len(circles)}/{MAX_STEPS})</b>\n\n"
        + "\n".join(lines)
        + "\n\n<i>Загрузить: отправьте кружочек → ответьте /setcircle N</i>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("users"), F.from_user.id == settings.admin_id)
async def cmd_users(message: Message):
    """Show all users with their info."""
    users = await get_all_users()

    if not users:
        await message.answer("Пока нет пользователей.")
        return

    lines = []
    for i, u in enumerate(users, 1):
        name = u["first_name"] or "—"
        username = f"@{u['username']}" if u["username"] else "нет username"
        step = u["funnel_step"]
        step_name = STEP_NAMES.get(step, "не начата")
        booked = "✅ записан" if u["booked"] else ""
        date = u["created_at"][:16] if u["created_at"] else ""

        lines.append(
            f"{i}. <b>{name}</b> ({username})\n"
            f"   ID: <code>{u['telegram_id']}</code>\n"
            f"   Воронка: шаг {step} ({step_name}) {booked}\n"
            f"   Пришёл: {date}"
        )

    # Telegram message limit is 4096 chars, split if needed
    header = f"👥 <b>Все пользователи ({len(users)})</b>\n\n"
    text = header + "\n\n".join(lines)

    if len(text) <= 4096:
        await message.answer(text)
    else:
        # Split into chunks
        await message.answer(header)
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 2 > 4000:
                await message.answer(chunk)
                chunk = ""
            chunk += line + "\n\n"
        if chunk:
            await message.answer(chunk)


@router.message(Command("broadcast"), F.from_user.id == settings.admin_id)
async def cmd_broadcast(message: Message):
    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.answer("Использование: /broadcast <текст сообщения>")
        return

    user_ids = await get_all_user_ids()
    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Рассылка завершена\nОтправлено: {sent}\nОшибок: {failed}")
