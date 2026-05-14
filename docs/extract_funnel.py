"""Extract and display complete funnel structure."""
from bot.i18n import get_text, get_funnel_step_text
from bot.services.scheduler import CIRCLE_STEPS, TEXT_STEPS

print("=" * 80)
print("ПОЛНАЯ СТРУКТУРА ВОРОНКИ LUNA WELLNESS BOT")
print("=" * 80)

print("\n" + "=" * 80)
print("ШАГИ С ВИДЕО-КРУЖКАМИ (1-7)")
print("=" * 80)

for delay, step in CIRCLE_STEPS:
    minutes = delay // 60
    if minutes == 0:
        timing = "Сразу после выбора языка"
    else:
        timing = f"+{minutes} мин от предыдущего"

    print(f"\n{'─' * 80}")
    print(f"ШАГ {step} | Время: {timing}")
    print(f"{'─' * 80}")
    print("\n🎥 ВИДЕО: Кружок отправляется\n")
    print("📱 РУССКИЙ:")
    print(get_funnel_step_text("ru", step))
    print("\n📱 УЗБЕКСКИЙ:")
    print(get_funnel_step_text("uz", step))

print("\n\n" + "=" * 80)
print("ТЕКСТОВЫЕ ШАГИ С РАЗВЕТВЛЕНИЕМ (8-12)")
print("=" * 80)

for delay, step, needs_branching in TEXT_STEPS:
    hours = delay // 3600
    days = delay // 86400
    if hours < 24:
        timing = f"+{hours}ч от предыдущего"
    else:
        timing = f"+{days} дней от предыдущего"

    print(f"\n{'─' * 80}")
    print(f"ШАГ {step} | Время: {timing}")
    if needs_branching:
        print("🔀 РАЗВЕТВЛЕНИЕ: Да (разные тексты для has_phone / no_phone)")
    else:
        print("📝 Только для пользователей БЕЗ номера телефона")
    print(f"{'─' * 80}")

    if needs_branching:
        # Вариант А: с телефоном
        print(f"\n✅ ВАРИАНТ А: Пользователь ОСТАВИЛ номер телефона")
        print("\n📱 РУССКИЙ:")
        print(get_text("ru", f"funnel_step_{step}_with_phone"))
        print("\n📱 УЗБЕКСКИЙ:")
        print(get_text("uz", f"funnel_step_{step}_with_phone"))

        # Вариант Б: без телефона
        print(f"\n❌ ВАРИАНТ Б: Пользователь НЕ оставил номер телефона")
        print("\n📱 РУССКИЙ:")
        print(get_text("ru", f"funnel_step_{step}_no_phone"))
        print("\n📱 УЗБЕКСКИЙ:")
        print(get_text("uz", f"funnel_step_{step}_no_phone"))
    else:
        # Только для no_phone
        print(f"\n❌ Только для пользователей БЕЗ номера")
        print("\n📱 РУССКИЙ:")
        print(get_funnel_step_text("ru", step))
        print("\n📱 УЗБЕКСКИЙ:")
        print(get_funnel_step_text("uz", step))

print("\n\n" + "=" * 80)
print("ДОПОЛНИТЕЛЬНЫЕ СООБЩЕНИЯ")
print("=" * 80)

print("\n📍 МГНОВЕННОЕ ПОДТВЕРЖДЕНИЕ (когда пользователь делится контактом)")
print("─" * 80)
print("\n📱 РУССКИЙ:")
print(get_text("ru", "contact_received"))
print("\n📱 УЗБЕКСКИЙ:")
print(get_text("uz", "contact_received"))

print("\n\n" + "=" * 80)
print("ТАЙМЕРЫ И ЛОГИКА")
print("=" * 80)

print("""
CIRCLE_STEPS (шаги 1-7):
  Шаг 1:  0 сек    → сразу после выбора языка
  Шаг 2:  240 сек  → +4 минуты
  Шаг 3:  600 сек  → +10 минут (14 мин от старта)
  Шаг 4:  900 сек  → +15 минут (29 мин от старта)
  Шаг 5:  1800 сек → +30 минут (59 мин от старта)
  Шаг 6:  3600 сек → +60 минут (2 часа от старта)
  Шаг 7:  7200 сек → +120 минут (4 часа от старта)

TEXT_STEPS (шаги 8-12):
  Шаг 8:  14400 сек  → +240 минут (8 часов от старта) [РАЗВЕТВЛЕНИЕ]
  Шаг 9:  57600 сек  → +960 минут (24 часа от старта) [РАЗВЕТВЛЕНИЕ]
  Шаг 10: 172800 сек → +48 часов (3 дня от шага 9) [ТОЛЬКО no_phone]
  Шаг 11: 172800 сек → +48 часов (5 дней от старта) [ТОЛЬКО no_phone]
  Шаг 12: 172800 сек → +48 часов (7 дней от старта) [ТОЛЬКО no_phone]

ЛОГИКА РАЗВЕТВЛЕНИЯ:
  - Шаги 1-7: ВСЕ пользователи получают (видео + текст)
  - Шаг 8:
    • Если has_phone → текст "спасибо что оставили контакт"
    • Если no_phone → текст с мягким призывом оставить номер
  - Шаг 9:
    • Если has_phone → текст "ждём вас на занятии"
    • Если no_phone → текст с предложением записаться
  - Шаги 10-12: ТОЛЬКО для no_phone (has_phone пропускают эти шаги)

ОСТАНОВКА ВОРОНКИ:
  - Если пользователь забронировал (booked=1) → воронка останавливается
  - Проверка перед КАЖДЫМ шагом
""")

print("\n" + "=" * 80)
print("КОНЕЦ ОТЧЁТА")
print("=" * 80)
