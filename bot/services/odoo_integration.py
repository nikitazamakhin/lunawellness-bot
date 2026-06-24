"""
Odoo CRM Integration Service
Автоматическое создание лидов в Odoo после бронирования в боте
"""

import aiohttp
import logging
from typing import Dict

from bot.config import settings

logger = logging.getLogger(__name__)

# Odoo API Configuration (загружается из .env файла через pydantic-settings)
ODOO_API_URL = settings.odoo_api_url
ODOO_API_TOKEN = settings.odoo_api_token

# Проверка наличия обязательных настроек
if not ODOO_API_URL or not ODOO_API_TOKEN:
    logger.warning(
        "⚠️ Odoo credentials not found in .env file. "
        "Integration will be disabled. Please set ODOO_API_URL and ODOO_API_TOKEN in .env file."
    )
    ODOO_INTEGRATION_ENABLED = False
else:
    ODOO_INTEGRATION_ENABLED = True
    logger.info(f"✅ Odoo integration enabled. API URL: {ODOO_API_URL}")


async def create_lead_in_odoo(
    course_name: str,
    weekday: str,
    name: str,
    phone: str,
    telegram_id: int
) -> Dict:
    """
    Создать лид в Odoo CRM.

    Args:
        course_name: Название курса (направление) - "Reformer Pilates", "Aerial Yoga", etc.
        weekday: День недели - "Понедельник", "Вторник", etc.
        name: Имя клиента
        phone: Телефон клиента (+998...)
        telegram_id: Telegram ID пользователя

    Returns:
        Dict с результатом:
        {
            "success": True/False,
            "lead_id": int,
            "lead_name": str,
            "contact_id": int,
            "contact_name": str,
            "error": str (если success=False)
        }
    """
    # Проверка, что интеграция включена
    if not ODOO_INTEGRATION_ENABLED:
        logger.warning(f"⚠️ Odoo integration disabled - skipping lead creation for {name} ({telegram_id})")
        return {
            "success": False,
            "error": "Odoo integration disabled (credentials not configured)"
        }

    url = f"{ODOO_API_URL}/crm/leads"

    payload = {
        "course_name": course_name,
        "weekday": weekday,
        "name": name,
        "phone": phone,
        "telegram_id": str(telegram_id)  # API требует string
    }

    params = {
        "token": ODOO_API_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:

                if response.status == 201:
                    data = await response.json()
                    logger.info(
                        f"✅ Lead created in Odoo: {data['lead_id']} | "
                        f"Contact: {data['contact_id']} | "
                        f"Telegram ID: {telegram_id}"
                    )
                    return {
                        "success": True,
                        "lead_id": data["lead_id"],
                        "lead_name": data["lead_name"],
                        "contact_id": data["contact_id"],
                        "contact_name": data["contact_name"]
                    }
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Failed to create lead in Odoo: "
                        f"Status {response.status} | "
                        f"Error: {error_text} | "
                        f"Telegram ID: {telegram_id}"
                    )
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }

    except aiohttp.ClientError as e:
        logger.error(f"❌ Network error while creating lead in Odoo: {e} | Telegram ID: {telegram_id}")
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }

    except Exception as e:
        logger.error(f"❌ Unexpected error while creating lead in Odoo: {e} | Telegram ID: {telegram_id}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


# Маппинг направлений из бота на course_name для Odoo
DIRECTION_MAPPING = {
    "Reformer Pilates": "Reformer Pilates",
    "Aerial Yoga": "Aerial Yoga",
    "Yoga": "Yoga",
    "Cycling": "Cycling",
    "Luna Shape": "Luna Shape",
    "SPA & Beauty": "SPA & Beauty"
}

# Маппинг дней недели (если нужно преобразование)
WEEKDAY_MAPPING_RU = {
    "Понедельник": "Понедельник",
    "Вторник": "Вторник",
    "Среда": "Среда",
    "Четверг": "Четверг",
    "Пятница": "Пятница",
    "Суббота": "Суббота",
    "Воскресенье": "Воскресенье"
}

WEEKDAY_MAPPING_UZ = {
    # Cyrillic Uzbek
    "Душанба": "Понедельник",
    "Сешанба": "Вторник",
    "Чоршанба": "Среда",
    "Пайшанба": "Четверг",
    "Жума": "Пятница",
    "Шанба": "Суббота",
    "Якшанба": "Воскресенье",
    # Latin Uzbek
    "Dushanba": "Понедельник",
    "Seshanba": "Вторник",
    "Chorshanba": "Среда",
    "Payshanba": "Четверг",
    "Juma": "Пятница",
    "Shanba": "Суббота",
    "Yakshanba": "Воскресенье",
}


def normalize_weekday(weekday: str) -> str:
    """
    Нормализовать день недели к формату Odoo.

    Args:
        weekday: День недели (может быть на узбекском)

    Returns:
        День недели на русском (для Odoo)
    """
    # Если уже на русском
    if weekday in WEEKDAY_MAPPING_RU:
        return WEEKDAY_MAPPING_RU[weekday]

    # Если на узбекском - преобразовать
    if weekday in WEEKDAY_MAPPING_UZ:
        return WEEKDAY_MAPPING_UZ[weekday]

    # Если не распознан - вернуть как есть
    return weekday


async def create_lead_from_booking(
    telegram_id: int,
    first_name: str,
    phone: str,
    direction: str,
    day: str
) -> Dict:
    """
    Удобная функция для создания лида из данных бронирования.

    Args:
        telegram_id: Telegram ID пользователя
        first_name: Имя пользователя
        phone: Телефон
        direction: Направление (из бота)
        day: День недели (из бота)

    Returns:
        Dict с результатом
    """
    # Нормализовать данные
    course_name = DIRECTION_MAPPING.get(direction, direction)
    weekday = normalize_weekday(day)

    # Создать лид
    return await create_lead_in_odoo(
        course_name=course_name,
        weekday=weekday,
        name=first_name,
        phone=phone,
        telegram_id=telegram_id
    )


async def create_interest_lead(telegram_id: int, first_name: str, phone: str) -> Dict:
    """Create Odoo lead for user who shared phone in funnel (no booking yet)."""
    return await create_lead_in_odoo(
        course_name="Интерес",
        weekday="—",
        name=first_name or "Клиент",
        phone=phone,
        telegram_id=telegram_id,
    )


# Пример использования:
"""
from bot.services.odoo_integration import create_lead_from_booking

# После успешного бронирования в боте:
result = await create_lead_from_booking(
    telegram_id=943359568,
    first_name="Анастасия",
    phone="+998901234567",
    direction="Reformer Pilates",
    day="Понедельник"
)

if result['success']:
    logger.info(f"Lead created: ID {result['lead_id']}")
else:
    logger.error(f"Failed to create lead: {result['error']}")
"""
