from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.i18n import get_text, get_direction_text
from bot.keyboards import (
    main_menu, directions_menu, direction_detail, schedule_menu, back_button, booking_cta,
)
from bot.database import log_event, get_user_language

router = Router()


@router.callback_query(F.data == "menu:back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "welcome"),
        reply_markup=main_menu(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:directions")
async def show_directions(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "directions_title"),
        parse_mode="HTML",
        reply_markup=directions_menu(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dir:"))
async def show_direction_detail(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    direction = callback.data.split(":")[1]
    text = get_direction_text(lang, direction)
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=direction_detail(lang, direction)
    )
    await log_event(callback.from_user.id, "view_direction", direction)
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def show_about(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "about"),
        parse_mode="HTML",
        reply_markup=back_button(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:schedule")
async def show_schedule_menu(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "schedule_menu_title"),
        parse_mode="HTML",
        reply_markup=schedule_menu(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "sched:schedule")
async def show_schedule(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "schedule"),
        parse_mode="HTML",
        reply_markup=back_button(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "sched:prices")
async def show_prices(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "prices"),
        parse_mode="HTML",
        reply_markup=back_button(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:promo")
async def show_promo(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "promo"),
        parse_mode="HTML",
        reply_markup=booking_cta(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:call")
async def show_call(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "call"),
        parse_mode="HTML",
        reply_markup=back_button(lang)
    )
    await callback.answer()
