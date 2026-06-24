"""All inline keyboards for LUNA bot."""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from bot.i18n import get_text


def language_selection() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")],
    ])


def phone_request(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_share_contact"), request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def phone_request_funnel(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Phone request keyboard used mid-funnel (has share contact button only)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_share_contact"), request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_directions"), callback_data="menu:directions")],
        [InlineKeyboardButton(text=get_text(lang, "btn_schedule"), callback_data="menu:schedule")],
        [InlineKeyboardButton(text=get_text(lang, "btn_about"), callback_data="menu:about")],
        [InlineKeyboardButton(text=get_text(lang, "btn_booking"), callback_data="menu:booking")],
        [InlineKeyboardButton(text=get_text(lang, "btn_call"), callback_data="menu:call")],
        [InlineKeyboardButton(text=get_text(lang, "btn_promo"), callback_data="menu:promo")],
    ])


def directions_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Reformer Pilates", callback_data="dir:reformer")],
        [InlineKeyboardButton(text="🪂 Aerial Yoga", callback_data="dir:aerial")],
        [InlineKeyboardButton(text="🧘 Yoga", callback_data="dir:yoga")],
        [InlineKeyboardButton(text="🚴 Cycling", callback_data="dir:cycling")],
        [InlineKeyboardButton(text="⚡ Luna Shape", callback_data="dir:shape")],
        [InlineKeyboardButton(text="💆 SPA & Beauty", callback_data="dir:spa")],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu:back")],
    ])


def direction_detail(lang: str = "ru", direction: str = "") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_register"), callback_data="menu:booking")],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu:directions")],
    ])


def schedule_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_schedule_view"), callback_data="sched:schedule")],
        [InlineKeyboardButton(text=get_text(lang, "btn_prices"), callback_data="sched:prices")],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu:back")],
    ])


def back_button(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_back_menu"), callback_data="menu:back")],
    ])


def booking_directions(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "dir_name_reformer"), callback_data="book:reformer")],
        [InlineKeyboardButton(text=get_text(lang, "dir_name_aerial"), callback_data="book:aerial")],
        [InlineKeyboardButton(text=get_text(lang, "dir_name_yoga"), callback_data="book:yoga")],
        [InlineKeyboardButton(text=get_text(lang, "dir_name_cycling"), callback_data="book:cycling")],
        [InlineKeyboardButton(text=get_text(lang, "dir_name_shape"), callback_data="book:shape")],
        [InlineKeyboardButton(text=get_text(lang, "dir_name_spa"), callback_data="book:spa")],
        [InlineKeyboardButton(text=get_text(lang, "btn_cancel"), callback_data="menu:back")],
    ])


def booking_days(lang: str = "ru") -> InlineKeyboardMarkup:
    day_keys = ["day_monday", "day_tuesday", "day_wednesday", "day_thursday", "day_friday", "day_saturday"]
    buttons = []
    for day_key in day_keys:
        day_text = get_text(lang, day_key)
        buttons.append([InlineKeyboardButton(text=day_text, callback_data=f"day:{day_text}")])
    buttons.append([InlineKeyboardButton(text=get_text(lang, "btn_cancel"), callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def booking_cta(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_register"), callback_data="menu:booking")],
    ])


def funnel_directions(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_directions"), callback_data="menu:directions")],
    ])
