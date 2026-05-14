"""Funnel scheduler — sends video circles + follow-up texts at intervals with branching logic."""

import asyncio
import logging

from aiogram import Bot

from bot.database import (
    update_funnel_step,
    is_booked,
    has_phone,
    log_event,
    get_incomplete_funnel_users,
    get_user_language,
)
from bot.i18n import get_funnel_step_text, get_text
from bot.keyboards import booking_cta
from bot.services.media import send_circle

logger = logging.getLogger(__name__)

# Steps 1-7: with video circles (everyone gets these)
CIRCLE_STEPS = [
    # (delay_sec, step_num)
    (0, 1),  # immediately (sent in start.py)
    (240, 2),  # +4 min
    (600, 3),  # +14 min (10 min from step 2)
    (900, 4),  # +29 min (15 min from step 3)
    (1800, 5),  # +59 min (30 min from step 4)
    (3600, 6),  # +2h (60 min from step 5)
    (7200, 7),  # +4h (120 min from step 6)
]

# Steps 8-12: text-only, with branching
TEXT_STEPS = [
    # (delay_sec, step_num, needs_branching)
    (14400, 8, True),  # +8h (240 min from step 7)
    (57600, 9, True),  # +24h total (960 min from step 8)
    (172800, 10, False),  # +3 days (only no_phone)
    (172800, 11, False),  # +5 days (48h from step 10, only no_phone)
    (172800, 12, False),  # +7 days (48h from step 11, only no_phone)
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
        if next_step <= 12:
            logger.info(f"Resuming funnel for {tid} from step {next_step}")
            await schedule_funnel(bot, tid, from_step=next_step)


async def _run_funnel(bot: Bot, telegram_id: int, from_step: int = 2):
    """Run funnel sequence with delays and branching logic."""

    # Run circle steps (1-7)
    for delay, step in CIRCLE_STEPS:
        if step < from_step:
            continue

        await asyncio.sleep(delay)

        if await is_booked(telegram_id):
            logger.info(f"User {telegram_id} booked — stopping funnel at step {step}")
            return

        try:
            lang = await get_user_language(telegram_id)

            # Send circle video
            circle_sent = await send_circle(bot, telegram_id, step)
            if circle_sent:
                await asyncio.sleep(3)

            # Send text
            text = get_funnel_step_text(lang, step)
            await bot.send_message(telegram_id, text, parse_mode="HTML")

            await update_funnel_step(telegram_id, step)
            await log_event(
                telegram_id,
                f"funnel_step_{step}",
                f"circle={'sent' if circle_sent else 'no_video'}",
            )
            logger.info(f"Funnel step {step} sent to {telegram_id}")

        except Exception as e:
            logger.warning(f"Funnel step {step} failed for {telegram_id}: {e}")
            return

    # Run text steps (8-12) with branching
    for delay, step, needs_branching in TEXT_STEPS:
        if step < from_step:
            continue

        await asyncio.sleep(delay)

        if await is_booked(telegram_id):
            logger.info(f"User {telegram_id} booked — stopping funnel at step {step}")
            return

        # Check if user has phone for branching
        user_has_phone = await has_phone(telegram_id)

        # Skip steps 10-12 if user has phone
        if step >= 10 and user_has_phone:
            logger.info(f"User {telegram_id} has phone — skipping step {step}")
            continue

        try:
            lang = await get_user_language(telegram_id)

            # Get appropriate text based on phone status
            if needs_branching:
                text_key = f"funnel_step_{step}_with_phone" if user_has_phone else f"funnel_step_{step}_no_phone"
                text = get_text(lang, text_key)
            else:
                text = get_funnel_step_text(lang, step)

            # Add booking button for no_phone users
            keyboard = booking_cta(lang) if not user_has_phone else None

            await bot.send_message(
                telegram_id, text, reply_markup=keyboard, parse_mode="HTML"
            )

            await update_funnel_step(telegram_id, step)
            await log_event(
                telegram_id,
                f"funnel_step_{step}",
                f"has_phone={user_has_phone}",
            )
            logger.info(
                f"Funnel step {step} sent to {telegram_id} (has_phone={user_has_phone})"
            )

        except Exception as e:
            logger.warning(f"Funnel step {step} failed for {telegram_id}: {e}")
            return
