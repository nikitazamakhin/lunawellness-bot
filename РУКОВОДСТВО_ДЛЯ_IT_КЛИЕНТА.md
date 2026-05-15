# 🔧 Руководство для IT-отдела LUNA: Интеграция бота с Odoo

## 📋 Цель

Подключить ваш Odoo CRM к существующему Telegram боту для автоматической синхронизации:
- Новых пользователей (лиды)
- Бронирований (сделки)
- Истории взаимодействий (события)

## ⚡ Главное: Бот УЖЕ работает!

Вам НЕ нужно:
- ❌ Разрабатывать бота
- ❌ Разрабатывать REST API
- ❌ Платить за доработки

Вам нужно только:
- ✅ Подключиться к базе данных бота
- ✅ Читать новые записи
- ✅ Создавать лиды/сделки в Odoo

---

## 🏗️ Текущая архитектура

```
┌─────────────────────────────────┐
│      Telegram Bot (Python)      │
│                                 │
│  - aiogram 3.15                 │
│  - Воронка из 12 шагов         │
│  - Бронирование                │
│  - Языки: RU + UZ              │
└─────────────┬───────────────────┘
              │
              ▼
     ┌──────────────────┐
     │   SQLite база    │
     │   (luna.db)      │
     │                  │
     │  • users         │
     │  • bookings      │
     │  • events        │
     │  • circles       │
     └──────────────────┘
```

**Где находится:**
- Сервер: VPS/локальный сервер UNIKA
- Путь к БД: `/path/to/luna-bot/data/luna.db`
- Размер БД: ~2-5 MB
- Обновления: в реальном времени

---

## 📊 Структура базы данных

### Таблица: `users`

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Автоинкремент ID |
| telegram_id | INTEGER | Уникальный ID Telegram (PRIMARY) |
| first_name | TEXT | Имя пользователя |
| username | TEXT | @username (может быть пустым) |
| language | TEXT | Язык (ru/uz) |
| funnel_step | INTEGER | Шаг воронки (0-12) |
| booked | INTEGER | Забронировал ли (0/1) |
| created_at | TIMESTAMP | Дата регистрации |

**Пример записи:**
```sql
telegram_id: 943359568
first_name: "Анастасия"
username: "nastya_fit"
language: "ru"
funnel_step: 6
booked: 0
created_at: "2026-05-10 14:30:00"
```

### Таблица: `bookings`

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | ID бронирования |
| telegram_id | INTEGER | ID пользователя (FK) |
| direction | TEXT | Направление (Reformer Pilates, Aerial Yoga...) |
| day | TEXT | День недели |
| name | TEXT | Имя клиента |
| phone | TEXT | Телефон |
| status | TEXT | Статус (new/confirmed/cancelled) |
| created_at | TIMESTAMP | Дата создания |

**Пример записи:**
```sql
id: 123
telegram_id: 943359568
direction: "Reformer Pilates"
day: "Понедельник"
name: "Анастасия"
phone: "+998901234567"
status: "new"
created_at: "2026-05-14 15:20:00"
```

### Таблица: `events`

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | ID события |
| telegram_id | INTEGER | ID пользователя |
| event_type | TEXT | Тип события |
| data | TEXT | Дополнительные данные |
| created_at | TIMESTAMP | Время события |

**Типы событий:**
- `start` — запустил бота
- `language_selected` — выбрал язык
- `funnel_step_N` — прошёл шаг N (1-12)
- `booking` — забронировал занятие

**Пример записи:**
```sql
id: 789
telegram_id: 943359568
event_type: "funnel_step_6"
data: "circle=sent"
created_at: "2026-05-10 16:30:00"
```

---

## 🔌 Варианты интеграции

### ✅ Вариант 1: Прямой доступ к базе (РЕКОМЕНДУЕМ)

**Как работает:**
1. UNIKA даёт вам доступ к файлу `luna.db`
2. Вы настраиваете cron job (каждые 5-15 минут)
3. Читаете новые записи из таблиц
4. Создаёте лиды/сделки в Odoo

**Преимущества:**
- ✅ Самый простой
- ✅ Не требует изменений в боте
- ✅ Полный контроль
- ✅ Можно внедрить за 1-2 дня

**Недостатки:**
- ⚠️ Задержка 5-15 минут (не реального времени)
- ⚠️ Нужен доступ к файлу БД

---

### ✅ Вариант 2: SSH + SQL запросы

**Как работает:**
1. UNIKA даёт SSH доступ к серверу
2. Вы подключаетесь к БД через SQLite CLI
3. Выполняете SQL запросы удалённо

**Преимущества:**
- ✅ Не нужно копировать файл
- ✅ Всегда актуальные данные
- ✅ Можно автоматизировать

**Недостатки:**
- ⚠️ Нужен SSH доступ

---

### ✅ Вариант 3: Webhook (в реальном времени)

**Как работает:**
1. UNIKA добавляет 10-15 строк кода в бота
2. Бот отправляет события на ваш endpoint
3. Вы получаете данные мгновенно

**Преимущества:**
- ✅ Реальное время (1-2 секунды)
- ✅ Не нужен доступ к серверу
- ✅ Безопасно

**Недостатки:**
- ⚠️ Нужны минимальные изменения в боте (1 час работы)

---

## 💻 Пример реализации: Вариант 1 (прямой доступ)

### Шаг 1: Получить доступ к luna.db

**Запросите у UNIKA:**
- Копию файла `luna.db` (для разработки)
- Путь к файлу на сервере (для production)
- Или SSH доступ для чтения

### Шаг 2: Установить Python библиотеки

```bash
pip install sqlite3  # Встроенная в Python
# или
pip install aiosqlite  # Для async
```

### Шаг 3: Синхронизация новых лидов

```python
import sqlite3
from datetime import datetime, timedelta

# Путь к базе (замените на актуальный)
DB_PATH = "/path/to/luna.db"

def get_new_users(since_minutes=15):
    """Получить пользователей, созданных за последние N минут."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Время 15 минут назад
    since_time = datetime.now() - timedelta(minutes=since_minutes)

    cursor.execute("""
        SELECT
            telegram_id,
            first_name,
            username,
            language,
            funnel_step,
            booked,
            created_at
        FROM users
        WHERE created_at >= ?
        ORDER BY created_at DESC
    """, (since_time.isoformat(),))

    users = cursor.fetchall()
    conn.close()

    return [dict(row) for row in users]


def create_odoo_lead(user):
    """Создать лид в Odoo из данных пользователя."""
    # Ваш код для создания лида в Odoo
    odoo_lead = odoo.create('crm.lead', {
        'name': user['first_name'],
        'contact_name': user['first_name'],
        'phone': '',  # Пока пустой, заполнится после бронирования
        'description': f"Telegram: @{user['username'] or 'без username'}",
        'source_id': 'Telegram Bot',  # Источник
        'stage_id': get_stage_by_funnel_step(user['funnel_step']),
        'tag_ids': [(4, get_tag_id(user['language']))],  # ru/uz
        'x_telegram_id': user['telegram_id'],  # Custom поле
    })

    return odoo_lead


def sync_users():
    """Основная функция синхронизации."""
    new_users = get_new_users(since_minutes=15)

    print(f"Найдено новых пользователей: {len(new_users)}")

    for user in new_users:
        # Проверить, не создан ли уже лид
        existing = odoo.search('crm.lead', [
            ('x_telegram_id', '=', user['telegram_id'])
        ])

        if not existing:
            lead = create_odoo_lead(user)
            print(f"✅ Создан лид для {user['first_name']} (ID: {lead.id})")
        else:
            print(f"⏭️  Лид уже существует для {user['first_name']}")


if __name__ == "__main__":
    sync_users()
```

### Шаг 4: Синхронизация бронирований

```python
def get_new_bookings(since_minutes=15):
    """Получить новые бронирования."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    since_time = datetime.now() - timedelta(minutes=since_minutes)

    cursor.execute("""
        SELECT
            b.id,
            b.telegram_id,
            b.direction,
            b.day,
            b.name,
            b.phone,
            b.status,
            b.created_at,
            u.first_name,
            u.username,
            u.language
        FROM bookings b
        LEFT JOIN users u ON b.telegram_id = u.telegram_id
        WHERE b.created_at >= ? AND b.status = 'new'
        ORDER BY b.created_at DESC
    """, (since_time.isoformat(),))

    bookings = cursor.fetchall()
    conn.close()

    return [dict(row) for row in bookings]


def create_odoo_opportunity(booking):
    """Создать сделку в Odoo."""
    # Найти или создать партнёра
    partner = odoo.search('res.partner', [
        ('phone', '=', booking['phone'])
    ])

    if not partner:
        partner = odoo.create('res.partner', {
            'name': booking['name'],
            'phone': booking['phone'],
            'comment': f"Telegram: @{booking['username'] or 'нет'}",
        })

    # Создать сделку
    opportunity = odoo.create('crm.lead', {
        'name': f"{booking['direction']} - {booking['name']}",
        'partner_id': partner.id,
        'phone': booking['phone'],
        'type': 'opportunity',
        'description': f"День: {booking['day']}\nИсточник: Telegram Bot",
        'x_telegram_id': booking['telegram_id'],
        'x_booking_id': booking['id'],
    })

    return opportunity


def sync_bookings():
    """Синхронизация бронирований."""
    new_bookings = get_new_bookings(since_minutes=15)

    print(f"Найдено новых бронирований: {len(new_bookings)}")

    for booking in new_bookings:
        existing = odoo.search('crm.lead', [
            ('x_booking_id', '=', booking['id'])
        ])

        if not existing:
            opp = create_odoo_opportunity(booking)
            print(f"✅ Создана сделка для {booking['name']}")
        else:
            print(f"⏭️  Сделка уже существует")
```

### Шаг 5: Настроить cron job

```bash
# Открыть crontab
crontab -e

# Добавить задачу (запуск каждые 15 минут)
*/15 * * * * /usr/bin/python3 /path/to/sync_luna_odoo.py >> /var/log/luna-sync.log 2>&1
```

---

## 📊 Полезные SQL запросы

### Получить всех пользователей
```sql
SELECT * FROM users ORDER BY created_at DESC;
```

### Получить новые бронирования
```sql
SELECT
    b.*,
    u.first_name,
    u.username
FROM bookings b
LEFT JOIN users u ON b.telegram_id = u.telegram_id
WHERE b.status = 'new'
ORDER BY b.created_at DESC;
```

### Получить пользователей на определённом шаге воронки
```sql
SELECT * FROM users
WHERE funnel_step = 6 AND booked = 0;
```

### Статистика: конверсия в бронирование
```sql
SELECT
    COUNT(*) as total_users,
    SUM(booked) as booked_users,
    ROUND(SUM(booked) * 100.0 / COUNT(*), 2) as conversion_rate
FROM users;
```

### Распределение по шагам воронки
```sql
SELECT
    funnel_step,
    COUNT(*) as count
FROM users
GROUP BY funnel_step
ORDER BY funnel_step;
```

### История пользователя
```sql
SELECT
    event_type,
    data,
    created_at
FROM events
WHERE telegram_id = 943359568
ORDER BY created_at;
```

---

## 🔔 Вариант 3: Webhook (опционально)

Если нужны обновления в реальном времени, UNIKA может добавить webhook в бота.

### Что нужно от вас:

**1. Предоставить endpoint URL:**
```
https://your-odoo.com/api/luna-webhook
```

**2. Принимать POST запросы:**

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your_secret_key"  # Получите от UNIKA

@app.route('/api/luna-webhook', methods=['POST'])
def luna_webhook():
    # Получить данные
    payload = request.get_data()
    signature = request.headers.get('X-Luna-Signature')

    # Проверить подпись (безопасность)
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if signature != expected:
        return {"error": "Invalid signature"}, 401

    # Обработать событие
    data = request.json
    event_type = data['event']

    if event_type == 'user.created':
        # Новый пользователь
        user = data['data']
        create_odoo_lead(user)

    elif event_type == 'booking.created':
        # Новое бронирование
        booking = data['data']
        create_odoo_opportunity(booking)

    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Формат событий:**

```json
{
  "event": "booking.created",
  "timestamp": "2026-05-14T16:15:00Z",
  "data": {
    "id": 123,
    "telegram_id": 943359568,
    "direction": "Reformer Pilates",
    "day": "Понедельник",
    "name": "Анастасия",
    "phone": "+998901234567",
    "user": {
      "first_name": "Анастасия",
      "username": "nastya_fit",
      "language": "ru"
    }
  }
}
```

---

## 🔧 Что нужно добавить в Odoo

### Custom поля в crm.lead:

```python
# В модели crm.lead добавить:
x_telegram_id = fields.Char('Telegram ID')
x_booking_id = fields.Integer('Booking ID')
x_funnel_step = fields.Integer('Funnel Step')
x_language = fields.Selection([
    ('ru', 'Русский'),
    ('uz', 'Узбекский')
], 'Language')
```

### Источник "Telegram Bot":

```python
# Создать источник лидов
odoo.create('utm.source', {
    'name': 'Telegram Bot'
})
```

### Теги для языков:

```python
odoo.create('crm.tag', {'name': 'RU'})
odoo.create('crm.tag', {'name': 'UZ'})
```

---

## 📋 Чеклист внедрения

### Подготовка (от UNIKA):
- [ ] Предоставить копию luna.db для разработки
- [ ] Предоставить SSH доступ (или путь к БД)
- [ ] Предоставить документацию по структуре БД
- [ ] Опционально: добавить webhook (1 час работы)

### Разработка (ваш IT-отдел):
- [ ] Изучить структуру базы данных
- [ ] Создать custom поля в Odoo (x_telegram_id, etc)
- [ ] Написать скрипт синхронизации пользователей
- [ ] Написать скрипт синхронизации бронирований
- [ ] Настроить cron job (каждые 15 минут)
- [ ] Протестировать на тестовых данных

### Тестирование:
- [ ] Создать тестового пользователя в боте
- [ ] Проверить создание лида в Odoo
- [ ] Создать тестовое бронирование
- [ ] Проверить создание сделки в Odoo
- [ ] Проверить маппинг всех полей

### Production:
- [ ] Переключиться на production БД
- [ ] Запустить синхронизацию
- [ ] Мониторинг логов 1 неделю
- [ ] Настроить алерты при ошибках

---

## ⏱️ Оценка времени

| Задача | Время |
|--------|-------|
| Изучение структуры БД | 2 часа |
| Настройка Odoo (custom поля) | 2 часа |
| Разработка скрипта синхронизации | 8 часов |
| Тестирование | 4 часа |
| Деплой + настройка cron | 2 часа |
| **ИТОГО** | **18 часов** (~3 дня) |

---

## 🆘 Что запросить у UNIKA

### Минимум (для старта):

1. **Копия luna.db** для разработки
2. **Документация** структуры БД (этот файл)
3. **Контакт** для технических вопросов

### Для production:

4. **SSH доступ** к серверу с ботом (read-only)
5. **Путь к базе** на production сервере
6. **Webhook secret** (если используете вариант 3)

### Опционально (если нужны изменения):

7. **Webhook endpoint** в боте (1 час работы UNIKA, бесплатно)
8. **Кастомные поля** в БД (если нужны дополнительные данные)

---

## ❓ FAQ

### 1. Безопасно ли читать напрямую из luna.db?
**Да**, если доступ read-only. База SQLite поддерживает множественное чтение.

### 2. Можно ли обновлять данные в базе?
**Не рекомендуется**. Только чтение. Если нужны обновления — используйте webhook.

### 3. Как часто обновляется база?
**В реальном времени**. Каждое действие пользователя записывается мгновенно.

### 4. Что если база недоступна?
Cron job пропустит итерацию, продолжит при следующем запуске.

### 5. Можно ли получать данные старше 15 минут?
**Да**. При первом запуске можете импортировать всю историю.

---

## 📞 Контакты

**Техническая поддержка:**
- Telegram: @ezhovnikita
- Email: nikita@unika.agency

**Для запроса доступов:**
Написать в Telegram с темой "LUNA Bot - доступ к БД"

---

**Готовы начать интеграцию! Доступы предоставим в течение 24 часов. 🚀**
