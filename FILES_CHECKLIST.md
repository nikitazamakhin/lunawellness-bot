# Checklist: Проверка файлов после внедрения i18n

## ✅ Новые файлы (должны существовать)

```bash
# Основной файл переводов
ls -lh bot/i18n.py

# Скрипты
ls -lh scripts/migrate_add_language.py
ls -lh scripts/test_i18n.py

# Документация
ls -lh MIGRATION_i18n.md
ls -lh QUICKSTART_i18n.md
ls -lh CHANGES_i18n.txt
ls -lh PROJECT_SUMMARY_i18n.txt
ls -lh FILES_CHECKLIST.md
```

## ✅ Изменённые файлы (должны содержать i18n импорты)

```bash
# Проверить импорт i18n в database.py
grep "language" bot/database.py

# Проверить импорт i18n в keyboards.py
grep "from bot.i18n import get_text" bot/keyboards.py

# Проверить импорт i18n в handlers/start.py
grep "from bot.i18n import" bot/handlers/start.py

# Проверить импорт i18n в handlers/menu.py
grep "from bot.i18n import" bot/handlers/menu.py

# Проверить импорт i18n в handlers/booking.py
grep "from bot.i18n import" bot/handlers/booking.py

# Проверить импорт i18n в services/scheduler.py
grep "from bot.i18n import" bot/services/scheduler.py
```

## ✅ Переименованные файлы

```bash
# Старый texts.py должен быть переименован
ls -lh bot/texts_old.py
# Проверить, что bot/texts.py НЕ существует
ls bot/texts.py 2>&1 | grep "No such file"
```

## ✅ Проверка синтаксиса Python

```bash
# Компиляция всех изменённых файлов
python3 -m py_compile \
  bot/i18n.py \
  bot/database.py \
  bot/keyboards.py \
  bot/handlers/start.py \
  bot/handlers/menu.py \
  bot/handlers/booking.py \
  bot/services/scheduler.py \
  scripts/migrate_add_language.py \
  scripts/test_i18n.py
```

## ✅ Запуск тестов

```bash
# Тест переводов
python3 scripts/test_i18n.py

# Миграция БД (если нужно)
python3 scripts/migrate_add_language.py
```

## ✅ Проверка структуры проекта

```bash
tree -L 3 -I '__pycache__|*.pyc|data|logs|media|temp_*' .
```

Ожидаемая структура:
```
.
├── CHANGES_i18n.txt
├── FILES_CHECKLIST.md
├── MIGRATION_i18n.md
├── PROJECT_SUMMARY_i18n.txt
├── QUICKSTART_i18n.md
├── bot
│   ├── handlers
│   │   ├── admin.py
│   │   ├── booking.py          [MODIFIED]
│   │   ├── menu.py             [MODIFIED]
│   │   └── start.py            [MODIFIED]
│   ├── services
│   │   ├── media.py
│   │   └── scheduler.py        [MODIFIED]
│   ├── config.py
│   ├── database.py             [MODIFIED]
│   ├── i18n.py                 [NEW]
│   ├── keyboards.py            [MODIFIED]
│   ├── main.py
│   └── texts_old.py            [RENAMED from texts.py]
└── scripts
    ├── migrate_add_language.py [NEW]
    └── test_i18n.py            [NEW]
```

## ✅ Быстрая проверка кода

```bash
# Проверить, что get_text импортирован где нужно
grep -r "get_text" bot/handlers/*.py bot/services/*.py bot/keyboards.py

# Проверить, что get_user_language используется
grep -r "get_user_language" bot/handlers/*.py bot/services/*.py

# Проверить, что set_user_language используется
grep -r "set_user_language" bot/handlers/*.py
```

## ✅ Финальная проверка

После выполнения всех пунктов выше:

- [ ] Все новые файлы существуют
- [ ] Все изменённые файлы содержат нужные импорты
- [ ] texts.py переименован в texts_old.py
- [ ] Все файлы компилируются без ошибок
- [ ] Тесты переводов проходят успешно
- [ ] Миграция БД завершена
- [ ] Структура проекта корректна
- [ ] Импорты i18n на месте

## 🚀 Готово к запуску!

```bash
# Запустить бота
python3 -m bot.main
```

Проверить с реальным пользователем:
1. Отправить `/start` с нового аккаунта
2. Выбрать язык (RU или UZ)
3. Проверить меню
4. Попробовать забронировать занятие
5. Проверить, что все сообщения на выбранном языке
