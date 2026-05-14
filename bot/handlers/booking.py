from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database import save_booking, mark_booked, log_event, get_user_language
from bot.i18n import get_text
from bot.keyboards import booking_directions, booking_days, main_menu, phone_request, ReplyKeyboardRemove
from bot.config import settings

router = Router()


class BookingForm(StatesGroup):
    direction = State()
    day = State()
    name = State()
    phone = State()


@router.callback_query(F.data == "menu:booking")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_language(callback.from_user.id)
    await state.update_data(lang=lang)
    await callback.message.edit_text(
        get_text(lang, "booking_start"),
        reply_markup=booking_directions(lang)
    )
    await state.set_state(BookingForm.direction)
    await callback.answer()


@router.callback_query(BookingForm.direction, F.data.startswith("book:"))
async def pick_direction(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    direction_key = callback.data.split(":")[1]
    direction_name = get_text(lang, f"dir_name_{direction_key}")
    await state.update_data(direction=direction_name)
    await callback.message.edit_text(
        get_text(lang, "booking_day"),
        reply_markup=booking_days(lang)
    )
    await state.set_state(BookingForm.day)
    await callback.answer()


@router.callback_query(BookingForm.day, F.data.startswith("day:"))
async def pick_day(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    day = callback.data.split(":")[1]
    await state.update_data(day=day)
    await callback.message.edit_text(get_text(lang, "booking_name"))
    await state.set_state(BookingForm.name)
    await callback.answer()


@router.message(BookingForm.name, F.text)
async def enter_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.update_data(name=message.text.strip())
    await message.answer(
        get_text(lang, "booking_phone"),
        reply_markup=phone_request(lang)
    )
    await state.set_state(BookingForm.phone)


@router.message(BookingForm.name)
async def enter_name_invalid(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await message.answer(get_text(lang, "booking_error_name"))


@router.message(BookingForm.phone, F.content_type == ContentType.CONTACT)
async def enter_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await _finish_booking(message, state, phone)


@router.message(BookingForm.phone, F.text)
async def enter_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    await _finish_booking(message, state, phone)


@router.message(BookingForm.phone)
async def enter_phone_invalid(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await message.answer(get_text(lang, "booking_error_phone"))


async def _finish_booking(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    direction = data["direction"]
    day = data["day"]
    name = data["name"]

    # Save to DB
    await save_booking(message.from_user.id, direction, day, name, phone)
    await mark_booked(message.from_user.id)
    await log_event(message.from_user.id, "booking", f"{direction} | {day}")

    # Send instant confirmation (removes reply keyboard)
    await message.answer(
        get_text(lang, "contact_received"),
        reply_markup=ReplyKeyboardRemove()
    )

    # Show booking details
    confirm_text = get_text(
        lang, "booking_confirm",
        direction=direction, day=day, name=name, phone=phone
    )
    await message.answer(confirm_text)

    # Show main menu
    await message.answer(
        get_text(lang, "booking_success_next"),
        reply_markup=main_menu(lang)
    )

    # Notify admin (always in Russian for admin)
    admin_text = get_text(
        "ru", "admin_new_booking",
        direction=direction,
        day=day,
        name=name,
        phone=phone,
        username=message.from_user.username or "—",
        telegram_id=message.from_user.id,
    )
    try:
        await message.bot.send_message(settings.admin_id, admin_text)
    except Exception:
        pass

    await state.clear()
