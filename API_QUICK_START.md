# 🚀 API Quick Start — Интеграция с Odoo

## Минимальная интеграция (30 минут)

### Шаг 1: Получить API ключ
```
Свяжитесь с командой LUNA для получения:
- API_KEY: luna_sk_xxxxxxxxxxxxx
- WEBHOOK_SECRET: whsec_xxxxxxxxxxxxx
```

### Шаг 2: Настроить webhook в Odoo
```python
# Odoo должен принимать POST запросы на:
https://your-odoo.com/api/luna-webhook

# С событиями:
- user.created → новый лид
- booking.created → новое бронирование
```

### Шаг 3: Протестировать подключение
```bash
curl -X GET https://api.lunawomensclub.uz/v1/health \
  -H "Authorization: Bearer luna_sk_xxxxxxxxxxxxx"
```

## 📊 Основные сценарии

### 1. Получить новые лиды (каждые 15 мин)
```python
import requests
from datetime import datetime, timedelta

API_KEY = "luna_sk_xxxxxxxxxxxxx"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Лиды за последние 15 минут
time_15min_ago = (datetime.now() - timedelta(minutes=15)).isoformat()

response = requests.get(
    "https://api.lunawomensclub.uz/v1/users",
    headers=headers,
    params={"created_after": time_15min_ago}
)

for user in response.json()["data"]:
    # Создать лид в Odoo
    odoo.create_lead({
        "name": user["first_name"],
        "phone": user.get("phone"),
        "source": "Telegram Bot",
        "telegram_id": user["telegram_id"]
    })
```

### 2. Получить новые бронирования
```python
response = requests.get(
    "https://api.lunawomensclub.uz/v1/bookings",
    headers=headers,
    params={"status": "new"}
)

for booking in response.json()["data"]:
    # Создать оппортюнити в Odoo
    odoo.create_opportunity({
        "partner_name": booking["name"],
        "phone": booking["phone"],
        "description": f"{booking['direction']} - {booking['day']}",
        "telegram_id": booking["telegram_id"]
    })

    # Подтвердить в боте
    requests.patch(
        f"https://api.lunawomensclub.uz/v1/bookings/{booking['id']}",
        headers=headers,
        json={"status": "confirmed"}
    )
```

### 3. Отправить напоминание клиенту
```python
requests.post(
    "https://api.lunawomensclub.uz/v1/messages/send",
    headers=headers,
    json={
        "telegram_id": 943359568,
        "text": "Напоминаем о вашем занятии завтра в 10:00!"
    }
)
```

## 🔔 Webhook пример

```python
from flask import Flask, request
import hmac, hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_xxxxxxxxxxxxx"

@app.route("/api/luna-webhook", methods=["POST"])
def webhook():
    # Проверка подписи
    signature = request.headers.get("X-Luna-Signature")
    payload = request.get_data()

    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if signature != expected:
        return {"error": "Invalid signature"}, 401

    # Обработка события
    data = request.json
    if data["event"] == "booking.created":
        booking = data["data"]
        # Создать в Odoo
        odoo.create_opportunity(booking)

    return {"status": "ok"}
```

## 📋 Чеклист внедрения

- [ ] Получить API ключ от LUNA
- [ ] Настроить webhook endpoint в Odoo
- [ ] Протестировать подключение (GET /health)
- [ ] Настроить синхронизацию новых лидов
- [ ] Настроить синхронизацию бронирований
- [ ] Настроить отправку уведомлений
- [ ] Добавить обработку ошибок
- [ ] Настроить логирование
- [ ] Запустить в production

## 🆘 Помощь

Полная документация: `API_SPECIFICATION.md`
Техподдержка: dev@lunawomensclub.uz
