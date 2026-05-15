# 🔌 API Спецификация для интеграции LUNA Bot с Odoo CRM

## 📋 Оглавление
1. [Обзор](#обзор)
2. [Аутентификация](#аутентификация)
3. [Endpoints](#endpoints)
4. [Webhooks](#webhooks)
5. [Модели данных](#модели-данных)
6. [Примеры использования](#примеры-использования)

---

## 🎯 Обзор

### Цель интеграции
Синхронизация данных между Telegram ботом LUNA Wellness и CRM Odoo для:
- Автоматического создания лидов
- Отслеживания воронки продаж
- Управления бронированиями
- Аналитики эффективности

### Архитектура
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Telegram    │ ◄─────► │  LUNA Bot    │ ◄─────► │   Odoo CRM   │
│   Users      │         │  (Python)    │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
                              │                          │
                              │    REST API              │
                              │    Webhooks              │
                              └──────────────────────────┘
```

### Базовый URL
```
Production:  https://api.lunawomensclub.uz/v1
Development: http://localhost:8000/v1
```

---

## 🔐 Аутентификация

### Метод: API Key (Bearer Token)

**Headers:**
```http
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

**Получение API ключа:**
1. Генерируется в админ-панели бота
2. Передаётся команде Odoo
3. Время жизни: 1 год (можно продлить)

**Пример запроса:**
```bash
curl -X GET https://api.lunawomensclub.uz/v1/users \
  -H "Authorization: Bearer luna_sk_1234567890abcdef" \
  -H "Content-Type: application/json"
```

**Ошибки аутентификации:**
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired API key"
}
```

---

## 📡 Endpoints

### 1. Пользователи (Leads)

#### 1.1. Получить всех пользователей
```http
GET /users
```

**Query Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| limit | integer | Лимит записей (default: 50, max: 100) |
| offset | integer | Смещение для пагинации (default: 0) |
| language | string | Фильтр по языку (ru/uz) |
| booked | boolean | Фильтр: забронировали или нет |
| funnel_step | integer | Фильтр по шагу воронки (0-12) |
| created_after | datetime | Созданы после даты (ISO 8601) |

**Response 200:**
```json
{
  "data": [
    {
      "telegram_id": 943359568,
      "first_name": "Анастасия",
      "username": "nastya_fit",
      "language": "ru",
      "funnel_step": 6,
      "booked": false,
      "created_at": "2026-05-10T14:30:00Z",
      "updated_at": "2026-05-14T10:15:00Z"
    }
  ],
  "meta": {
    "total": 156,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

#### 1.2. Получить пользователя по ID
```http
GET /users/{telegram_id}
```

**Response 200:**
```json
{
  "telegram_id": 943359568,
  "first_name": "Анастасия",
  "username": "nastya_fit",
  "language": "ru",
  "funnel_step": 6,
  "booked": false,
  "created_at": "2026-05-10T14:30:00Z",
  "updated_at": "2026-05-14T10:15:00Z",
  "events": [
    {
      "event_type": "start",
      "data": "",
      "created_at": "2026-05-10T14:30:00Z"
    },
    {
      "event_type": "language_selected",
      "data": "ru",
      "created_at": "2026-05-10T14:30:05Z"
    },
    {
      "event_type": "funnel_step_6",
      "data": "circle=sent",
      "created_at": "2026-05-10T16:30:00Z"
    }
  ],
  "bookings": []
}
```

**Response 404:**
```json
{
  "error": "not_found",
  "message": "User not found"
}
```

#### 1.3. Обновить пользователя
```http
PATCH /users/{telegram_id}
```

**Request Body:**
```json
{
  "odoo_lead_id": "12345",
  "notes": "Клиент заинтересован в Reformer Pilates"
}
```

**Response 200:**
```json
{
  "telegram_id": 943359568,
  "odoo_lead_id": "12345",
  "notes": "Клиент заинтересован в Reformer Pilates",
  "updated_at": "2026-05-14T15:30:00Z"
}
```

---

### 2. Бронирования (Bookings)

#### 2.1. Получить все бронирования
```http
GET /bookings
```

**Query Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| limit | integer | Лимит записей (default: 50) |
| offset | integer | Смещение для пагинации |
| status | string | Фильтр по статусу (new/confirmed/cancelled) |
| direction | string | Направление (reformer/aerial/yoga/cycling/shape/spa) |
| created_after | datetime | Созданы после даты |

**Response 200:**
```json
{
  "data": [
    {
      "id": 123,
      "telegram_id": 943359568,
      "direction": "Reformer Pilates",
      "day": "Понедельник",
      "name": "Анастасия",
      "phone": "+998901234567",
      "status": "new",
      "created_at": "2026-05-14T15:20:00Z",
      "user": {
        "telegram_id": 943359568,
        "first_name": "Анастасия",
        "username": "nastya_fit",
        "language": "ru"
      }
    }
  ],
  "meta": {
    "total": 45,
    "limit": 50,
    "offset": 0
  }
}
```

#### 2.2. Получить бронирование по ID
```http
GET /bookings/{id}
```

**Response 200:**
```json
{
  "id": 123,
  "telegram_id": 943359568,
  "direction": "Reformer Pilates",
  "day": "Понедельник",
  "name": "Анастасия",
  "phone": "+998901234567",
  "status": "new",
  "created_at": "2026-05-14T15:20:00Z",
  "odoo_booking_id": null,
  "user": {
    "telegram_id": 943359568,
    "first_name": "Анастасия",
    "username": "nastya_fit",
    "language": "ru",
    "funnel_step": 6,
    "booked": true
  }
}
```

#### 2.3. Обновить статус бронирования
```http
PATCH /bookings/{id}
```

**Request Body:**
```json
{
  "status": "confirmed",
  "odoo_booking_id": "OPP-12345",
  "scheduled_datetime": "2026-05-20T10:00:00Z",
  "notes": "Клиент подтверждён, место забронировано"
}
```

**Response 200:**
```json
{
  "id": 123,
  "status": "confirmed",
  "odoo_booking_id": "OPP-12345",
  "scheduled_datetime": "2026-05-20T10:00:00Z",
  "notes": "Клиент подтверждён, место забронировано",
  "updated_at": "2026-05-14T15:45:00Z"
}
```

#### 2.4. Отправить сообщение пользователю после подтверждения
```http
POST /bookings/{id}/notify
```

**Request Body:**
```json
{
  "message_template": "booking_confirmed",
  "variables": {
    "date": "20 мая",
    "time": "10:00",
    "trainer": "Елена"
  }
}
```

**Response 200:**
```json
{
  "success": true,
  "message_sent": true,
  "telegram_message_id": 456
}
```

---

### 3. События (Analytics)

#### 3.1. Получить события пользователя
```http
GET /users/{telegram_id}/events
```

**Query Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| event_type | string | Фильтр по типу события |
| created_after | datetime | События после даты |
| limit | integer | Лимит записей |

**Response 200:**
```json
{
  "data": [
    {
      "id": 789,
      "telegram_id": 943359568,
      "event_type": "funnel_step_6",
      "data": "circle=sent",
      "created_at": "2026-05-10T16:30:00Z"
    },
    {
      "id": 790,
      "telegram_id": 943359568,
      "event_type": "booking",
      "data": "Reformer Pilates | Понедельник",
      "created_at": "2026-05-14T15:20:00Z"
    }
  ],
  "meta": {
    "total": 12
  }
}
```

#### 3.2. Получить статистику воронки
```http
GET /analytics/funnel
```

**Query Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| date_from | date | Начало периода |
| date_to | date | Конец периода |

**Response 200:**
```json
{
  "period": {
    "from": "2026-05-01",
    "to": "2026-05-14"
  },
  "total_users": 156,
  "booked_users": 45,
  "conversion_rate": 28.8,
  "funnel_breakdown": {
    "step_0": 156,
    "step_1": 156,
    "step_2": 152,
    "step_3": 148,
    "step_4": 143,
    "step_5": 138,
    "step_6": 132,
    "step_7": 125,
    "step_8": 98,
    "step_9": 76,
    "step_10": 32,
    "step_11": 18,
    "step_12": 8
  },
  "conversion_by_step": {
    "step_1_to_2": 97.4,
    "step_2_to_3": 97.4,
    "step_3_to_4": 96.6,
    "step_8_to_booking": 46.0
  },
  "bookings_by_direction": {
    "Reformer Pilates": 18,
    "Aerial Yoga": 12,
    "Cycling": 8,
    "Yoga": 4,
    "Luna Shape": 2,
    "SPA": 1
  }
}
```

#### 3.3. Получить статистику по языкам
```http
GET /analytics/languages
```

**Response 200:**
```json
{
  "total_users": 156,
  "by_language": {
    "ru": {
      "count": 98,
      "percentage": 62.8,
      "booked": 32,
      "conversion": 32.7
    },
    "uz": {
      "count": 58,
      "percentage": 37.2,
      "booked": 13,
      "conversion": 22.4
    }
  }
}
```

---

### 4. Отправка сообщений

#### 4.1. Отправить произвольное сообщение
```http
POST /messages/send
```

**Request Body:**
```json
{
  "telegram_id": 943359568,
  "text": "Здравствуйте, Анастасия! Напоминаем о вашем занятии завтра в 10:00",
  "parse_mode": "HTML",
  "reply_markup": {
    "inline_keyboard": [
      [
        {
          "text": "Подтвердить",
          "callback_data": "confirm_123"
        },
        {
          "text": "Отменить",
          "callback_data": "cancel_123"
        }
      ]
    ]
  }
}
```

**Response 200:**
```json
{
  "success": true,
  "message_id": 789,
  "sent_at": "2026-05-14T16:00:00Z"
}
```

**Response 400:**
```json
{
  "error": "bad_request",
  "message": "User blocked the bot"
}
```

#### 4.2. Отправить шаблонное сообщение
```http
POST /messages/send-template
```

**Request Body:**
```json
{
  "telegram_id": 943359568,
  "template": "booking_reminder",
  "language": "ru",
  "variables": {
    "name": "Анастасия",
    "direction": "Reformer Pilates",
    "date": "15 мая",
    "time": "10:00"
  }
}
```

**Доступные шаблоны:**
- `booking_confirmed` — подтверждение бронирования
- `booking_reminder` — напоминание за день
- `booking_cancelled` — отмена бронирования
- `special_offer` — специальное предложение

---

### 5. Система (Health Check)

#### 5.1. Проверка работоспособности
```http
GET /health
```

**Response 200:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "bot": {
    "username": "Luna_Wellness_bot",
    "is_running": true,
    "last_update": "2026-05-14T16:05:00Z"
  },
  "database": {
    "status": "connected",
    "total_users": 156,
    "total_bookings": 45
  }
}
```

---

## 🔔 Webhooks

### Настройка Webhook
Odoo должен предоставить URL для получения событий:
```
https://your-odoo-instance.com/api/luna-webhook
```

### События

#### 1. Новый пользователь
**Event:** `user.created`

**Payload:**
```json
{
  "event": "user.created",
  "timestamp": "2026-05-14T16:10:00Z",
  "data": {
    "telegram_id": 943359568,
    "first_name": "Анастасия",
    "username": "nastya_fit",
    "language": "ru",
    "created_at": "2026-05-14T16:10:00Z"
  }
}
```

#### 2. Новое бронирование
**Event:** `booking.created`

**Payload:**
```json
{
  "event": "booking.created",
  "timestamp": "2026-05-14T16:15:00Z",
  "data": {
    "id": 124,
    "telegram_id": 943359568,
    "direction": "Reformer Pilates",
    "day": "Понедельник",
    "name": "Анастасия",
    "phone": "+998901234567",
    "status": "new",
    "user": {
      "first_name": "Анастасия",
      "username": "nastya_fit",
      "language": "ru"
    }
  }
}
```

#### 3. Прогресс по воронке
**Event:** `funnel.step_completed`

**Payload:**
```json
{
  "event": "funnel.step_completed",
  "timestamp": "2026-05-14T16:20:00Z",
  "data": {
    "telegram_id": 943359568,
    "funnel_step": 7,
    "previous_step": 6,
    "time_on_step": 7200,
    "user": {
      "first_name": "Анастасия",
      "language": "ru",
      "booked": false
    }
  }
}
```

#### 4. Изменение статуса бронирования
**Event:** `booking.status_changed`

**Payload:**
```json
{
  "event": "booking.status_changed",
  "timestamp": "2026-05-14T16:25:00Z",
  "data": {
    "id": 124,
    "telegram_id": 943359568,
    "old_status": "new",
    "new_status": "confirmed",
    "changed_by": "odoo_api"
  }
}
```

### Webhook Security

**Signature Verification:**
Каждый webhook содержит заголовок `X-Luna-Signature`:
```
X-Luna-Signature: sha256=abc123def456...
```

**Проверка подписи (Python):**
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 📊 Модели данных

### User
```typescript
{
  telegram_id: number;        // Уникальный ID Telegram
  first_name: string;         // Имя
  username: string | null;    // @username (может отсутствовать)
  language: "ru" | "uz";      // Язык
  funnel_step: number;        // 0-12
  booked: boolean;            // Забронировал ли
  created_at: datetime;       // Дата регистрации
  updated_at: datetime;       // Последнее обновление
  odoo_lead_id?: string;      // ID лида в Odoo (опционально)
  notes?: string;             // Заметки (опционально)
}
```

### Booking
```typescript
{
  id: number;                 // Уникальный ID бронирования
  telegram_id: number;        // ID пользователя
  direction: string;          // Направление
  day: string;                // День недели
  name: string;               // Имя клиента
  phone: string;              // Телефон
  status: "new" | "confirmed" | "cancelled";
  created_at: datetime;       // Дата создания
  odoo_booking_id?: string;   // ID в Odoo
  scheduled_datetime?: datetime; // Запланированное время
  notes?: string;             // Заметки
}
```

### Event
```typescript
{
  id: number;                 // ID события
  telegram_id: number;        // ID пользователя
  event_type: string;         // Тип события
  data: string;               // Данные (JSON string)
  created_at: datetime;       // Время события
}
```

**Типы событий:**
- `start` — запуск бота
- `language_selected` — выбран язык
- `funnel_step_N` — пройден шаг N воронки
- `booking` — создано бронирование
- `button_click` — нажата кнопка в меню

---

## 🔨 Примеры использования

### Пример 1: Получить новые лиды
```python
import requests

API_KEY = "luna_sk_1234567890abcdef"
BASE_URL = "https://api.lunawomensclub.uz/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Получить пользователей, созданных за последние 24 часа
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).isoformat()

response = requests.get(
    f"{BASE_URL}/users",
    headers=headers,
    params={
        "created_after": yesterday,
        "limit": 100
    }
)

users = response.json()["data"]
for user in users:
    print(f"New lead: {user['first_name']} (@{user['username']})")
```

### Пример 2: Обработать новое бронирование
```python
# Получить новые бронирования
response = requests.get(
    f"{BASE_URL}/bookings",
    headers=headers,
    params={"status": "new"}
)

bookings = response.json()["data"]

for booking in bookings:
    # Создать лид в Odoo
    odoo_lead = create_odoo_lead(booking)

    # Обновить бронирование с Odoo ID
    requests.patch(
        f"{BASE_URL}/bookings/{booking['id']}",
        headers=headers,
        json={
            "odoo_booking_id": odoo_lead["id"],
            "status": "confirmed"
        }
    )

    # Отправить уведомление клиенту
    requests.post(
        f"{BASE_URL}/bookings/{booking['id']}/notify",
        headers=headers,
        json={
            "message_template": "booking_confirmed",
            "variables": {
                "date": "20 мая",
                "time": "10:00"
            }
        }
    )
```

### Пример 3: Webhook handler (FastAPI)
```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()
WEBHOOK_SECRET = "your_webhook_secret"

@app.post("/api/luna-webhook")
async def handle_webhook(request: Request):
    # Получить payload
    payload = await request.body()
    signature = request.headers.get("X-Luna-Signature")

    # Проверить подпись
    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Обработать событие
    data = await request.json()
    event_type = data["event"]

    if event_type == "booking.created":
        # Создать лид в Odoo
        booking = data["data"]
        create_odoo_lead(booking)

    elif event_type == "funnel.step_completed":
        # Обновить статус лида
        user_data = data["data"]
        update_odoo_lead_stage(user_data)

    return {"status": "ok"}

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 📝 Rate Limits

| Endpoint | Лимит |
|----------|-------|
| GET запросы | 1000 req/hour |
| POST/PATCH | 500 req/hour |
| Webhooks | unlimited |

**При превышении:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 3600 seconds",
  "retry_after": 3600
}
```

---

## 🆘 Поддержка

**Техническая документация:** https://docs.lunawomensclub.uz/api
**Email:** dev@lunawomensclub.uz
**Telegram:** @luna_dev_support

---

**Версия:** 1.0.0
**Дата:** 2026-05-14
**Статус:** Ready for Implementation
