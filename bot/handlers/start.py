import asyncio
import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.config import settings
from bot.database import (
    get_or_create_user, log_event, update_funnel_step,
    set_user_language, get_user_language,
    save_user_phone, get_user_phone,
)
from bot.i18n import get_text, get_funnel_step_text
from bot.keyboards import main_menu, language_selection
from bot.services.scheduler import schedule_funnel
from bot.services.media import send_circle

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name or "",
        username=message.from_user.username or "",
    )
    await log_event(message.from_user.id, "start")

    tid = message.from_user.id

    # Новый пользователь - показать выбор языка
    if user["funnel_step"] == 0:
        await message.answer(
            get_text("ru", "select_language"),
            reply_markup=language_selection()
        )
    else:
        # Повторный /start — просто меню на выбранном языке
        lang = await get_user_language(tid)
        await message.answer(
            get_text(lang, "welcome"),
            reply_markup=main_menu(lang)
        )


@router.callback_query(F.data.startswith("lang:"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    """Handle language selection."""
    lang = callback.data.split(":")[1]
    tid = callback.from_user.id

    # Save language
    await set_user_language(tid, lang)
    await log_event(tid, "language_selected", lang)

    # Notify about language change
    await callback.answer(get_text(lang, "language_selected"))

    # Notify admin about new user
    name = callback.from_user.first_name or "—"
    username = f"@{callback.from_user.username}" if callback.from_user.username else "нет username"
    try:
        await callback.bot.send_message(
            settings.admin_id,
            f"🆕 <b>Новый пользователь!</b>\n\n"
            f"👤 {name} ({username})\n"
            f"🆔 <code>{tid}</code>\n"
            f"🌐 Язык: {lang.upper()}",
        )
    except Exception:
        pass

    # 1. Кружочек #1 — сразу
    circle_sent = await send_circle(callback.bot, tid, 1)
    if circle_sent:
        await asyncio.sleep(3)

    # 2. Текст шага 1 на выбранном языке
    await callback.bot.send_message(tid, get_funnel_step_text(lang, 1))
    await update_funnel_step(tid, 1)
    await log_event(tid, "funnel_step_1",
                    f"circle={'sent' if circle_sent else 'no_video'}")

    await asyncio.sleep(2)

    # 3. Приветствие + меню на выбранном языке
    await callback.message.edit_text(
        get_text(lang, "welcome"),
        reply_markup=main_menu(lang)
    )

    # Воронка продолжается со 2-го шага
    await schedule_funnel(callback.bot, tid)


@router.message(StateFilter(None), F.content_type == ContentType.CONTACT)
async def handle_funnel_contact(message: Message, state: FSMContext):
    """Handle phone number shared in funnel (outside booking FSM)."""
    phone = message.contact.phone_number

    # Skip if already have phone
    existing = await get_user_phone(message.from_user.id)
    if existing:
        lang = await get_user_language(message.from_user.id)
        await message.answer(get_text(lang, "funnel_phone_received"), reply_markup=ReplyKeyboardRemove())
        return

    await save_user_phone(message.from_user.id, phone)
    await log_event(message.from_user.id, "funnel_phone", phone)

    # Create Odoo interest lead
    try:
        from bot.services.odoo_integration import create_interest_lead
        result = await create_interest_lead(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name or "",
            phone=phone,
        )
        if result["success"]:
            logger.info(f"✅ Interest lead: {result['lead_id']} | {phone}")
        else:
            logger.warning(f"Interest lead failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Interest lead exception: {e}")

    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text(lang, "funnel_phone_received"), reply_markup=ReplyKeyboardRemove())

    # Notify admin
    try:
        name = message.from_user.first_name or "—"
        username = f"@{message.from_user.username}" if message.from_user.username else "нет username"
        await message.bot.send_message(
            settings.admin_id,
            f"📱 <b>Номер в воронке!</b>\n\n"
            f"👤 {name} ({username})\n"
            f"📱 {phone}\n"
            f"🆔 <code>{message.from_user.id}</code>",
        )
    except Exception:
        pass
