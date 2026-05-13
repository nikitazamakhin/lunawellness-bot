"""Funnel scheduler — sends video circles + follow-up texts at intervals."""

import asyncio
import logging

from aiogram import Bot

from bot.database import update_funnel_step, is_booked, log_event, get_incomplete_funnel_users, get_user_language
from bot.i18n import get_funnel_step_text
from bot.keyboards import funnel_directions, booking_cta
from bot.services.media import send_circle

logger = logging.getLogger(__name__)

ALL_STEPS = [
    # (delay_sec, step_num, keyboard_factory)
    (0,      1, lambda lang: None),                          # сразу (отправляется в start.py)
    (240,    2, lambda lang: None),                          # +4 мин
    (600,    3, lambda lang: funnel_directions(lang)),       # +14 мин
    (900,    4, lambda lang: None),                          # +29 мин
    (1800,   5, lambda lang: None),                          # +59 мин
    (3600,   6, lambda lang: None),                          # +2 ч
    (7200,   7, lambda lang: None),                          # +4 ч
    (14400,  8, lambda lang: booking_cta(lang)),             # +8 ч
    (28800,  9, lambda lang: booking_cta(lang)),             # +16 ч
    (28800, 10, lambda lang: booking_cta(lang)),             # +24 ч
]


async def schedule_funnel(bot: Bot, telegram_id: int, from_step: int = 2):
    """Schedule funnel messages for a user starting from given step."""
    asyncio.create_task(_run_funnel(bot, telegram_id, from_step))


async def resume_funnels(bot: Bot):
    """Resume incomplete funnels after bot restart."""
    users = await get_incomplete_funnel_users()
    for user in users:
        tid = user["telegram_id"]
        next_step = user["funnel_step"] + 1
        if next_step <= 10:
            logger.info(f"Resuming funnel for {tid} from step {next_step}")
            await schedule_funnel(bot, tid, from_step=next_step)


async def _run_funnel(bot: Bot, telegram_id: int, from_step: int = 2):
    """Run funnel sequence with delays starting from a specific step."""
    steps = [
        (delay, step, kb_factory)
        for delay, step, kb_factory in ALL_STEPS
        if step >= from_step
    ]

    for delay, step, kb_factory in steps:
        await asyncio.sleep(delay)

        if await is_booked(telegram_id):
            logger.info(f"User {telegram_id} booked — stopping funnel at step {step}")
            return

        try:
            # Get user language
            lang = await get_user_language(telegram_id)

            circle_sent = await send_circle(bot, telegram_id, step)
            if circle_sent:
                await asyncio.sleep(3)

            text = get_funnel_step_text(lang, step)
            keyboard = kb_factory(lang)
            await bot.send_message(
                telegram_id, text, reply_markup=keyboard
            )
            await update_funnel_step(telegram_id, step)
            await log_event(telegram_id, f"funnel_step_{step}",
                           f"circle={'sent' if circle_sent else 'no_video'}")
            logger.info(f"Funnel step {step} sent to {telegram_id}")
        except Exception as e:
            logger.warning(f"Funnel step {step} failed for {telegram_id}: {e}")
            return
