-- ============================================
-- LUNA Wellness Bot - Database Schema
-- ============================================
-- SQLite database structure
-- File: luna.db
-- Location: /data/luna.db
-- ============================================

-- ============================================
-- Таблица: users
-- Описание: Все пользователи бота
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,      -- Telegram User ID (уникальный)
    first_name TEXT DEFAULT '',               -- Имя пользователя
    username TEXT DEFAULT '',                 -- @username (может быть пустым)
    language TEXT DEFAULT 'ru',               -- Язык (ru/uz)
    funnel_step INTEGER DEFAULT 0,            -- Шаг воронки (0-12)
    booked INTEGER DEFAULT 0,                 -- Забронировал ли (0/1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_booked ON users(booked);
CREATE INDEX IF NOT EXISTS idx_users_funnel_step ON users(funnel_step);

-- ============================================
-- Таблица: bookings
-- Описание: Бронирования занятий
-- ============================================
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,             -- ID пользователя (FK → users)
    direction TEXT NOT NULL,                  -- Направление (Reformer Pilates, Aerial Yoga, etc)
    day TEXT NOT NULL,                        -- День недели (Понедельник, Вторник, etc)
    name TEXT NOT NULL,                       -- Имя клиента
    phone TEXT NOT NULL,                      -- Телефон
    status TEXT DEFAULT 'new',                -- Статус (new/confirmed/cancelled)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_bookings_telegram_id ON bookings(telegram_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);

-- ============================================
-- Таблица: events
-- Описание: События/действия пользователей
-- ============================================
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,             -- ID пользователя
    event_type TEXT NOT NULL,                 -- Тип события
    data TEXT DEFAULT '',                     -- Дополнительные данные (JSON string)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Время события
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_events_telegram_id ON events(telegram_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);

-- ============================================
-- Таблица: circles
-- Описание: Видео-кружки (file_id для переиспользования)
-- ============================================
CREATE TABLE IF NOT EXISTS circles (
    step INTEGER PRIMARY KEY,                 -- Номер шага (1-7)
    file_id TEXT NOT NULL                     -- Telegram file_id
);

-- ============================================
-- ПРИМЕРЫ ДАННЫХ
-- ============================================

-- Пример: пользователь
-- INSERT INTO users (telegram_id, first_name, username, language, funnel_step, booked)
-- VALUES (943359568, 'Анастасия', 'nastya_fit', 'ru', 6, 0);

-- Пример: бронирование
-- INSERT INTO bookings (telegram_id, direction, day, name, phone, status)
-- VALUES (943359568, 'Reformer Pilates', 'Понедельник', 'Анастасия', '+998901234567', 'new');

-- Пример: событие
-- INSERT INTO events (telegram_id, event_type, data)
-- VALUES (943359568, 'funnel_step_6', 'circle=sent');

-- ============================================
-- ПОЛЕЗНЫЕ ЗАПРОСЫ ДЛЯ ODOO
-- ============================================

-- 1. Получить новых пользователей за последние 15 минут
/*
SELECT
    telegram_id,
    first_name,
    username,
    language,
    funnel_step,
    booked,
    created_at
FROM users
WHERE created_at >= datetime('now', '-15 minutes')
ORDER BY created_at DESC;
*/

-- 2. Получить новые бронирования
/*
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
WHERE b.status = 'new'
ORDER BY b.created_at DESC;
*/

-- 3. Получить полную историю пользователя
/*
SELECT
    u.telegram_id,
    u.first_name,
    u.username,
    u.language,
    u.funnel_step,
    u.booked,
    u.created_at as registered_at,
    (
        SELECT json_group_array(
            json_object(
                'event', event_type,
                'data', data,
                'time', created_at
            )
        )
        FROM events e
        WHERE e.telegram_id = u.telegram_id
        ORDER BY e.created_at
    ) as events,
    (
        SELECT json_group_array(
            json_object(
                'direction', direction,
                'day', day,
                'phone', phone,
                'status', status,
                'time', created_at
            )
        )
        FROM bookings b
        WHERE b.telegram_id = u.telegram_id
        ORDER BY b.created_at
    ) as bookings
FROM users u
WHERE u.telegram_id = ?;
*/

-- 4. Статистика: конверсия в бронирование
/*
SELECT
    COUNT(*) as total_users,
    SUM(booked) as booked_users,
    ROUND(SUM(booked) * 100.0 / COUNT(*), 2) as conversion_rate,
    COUNT(CASE WHEN language = 'ru' THEN 1 END) as ru_users,
    COUNT(CASE WHEN language = 'uz' THEN 1 END) as uz_users
FROM users;
*/

-- 5. Распределение по шагам воронки
/*
SELECT
    funnel_step,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users), 2) as percentage
FROM users
GROUP BY funnel_step
ORDER BY funnel_step;
*/

-- 6. Пользователи, которые "застряли" на определённом шаге
/*
SELECT
    telegram_id,
    first_name,
    username,
    funnel_step,
    created_at,
    ROUND((julianday('now') - julianday(created_at)) * 24) as hours_since_registration
FROM users
WHERE funnel_step BETWEEN 1 AND 11
  AND booked = 0
  AND created_at < datetime('now', '-24 hours')
ORDER BY created_at;
*/

-- 7. Топ направлений по бронированиям
/*
SELECT
    direction,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM bookings), 2) as percentage
FROM bookings
GROUP BY direction
ORDER BY count DESC;
*/

-- 8. Время от регистрации до бронирования
/*
SELECT
    u.telegram_id,
    u.first_name,
    u.created_at as registered,
    b.created_at as booked,
    ROUND((julianday(b.created_at) - julianday(u.created_at)) * 24, 2) as hours_to_book
FROM users u
INNER JOIN bookings b ON u.telegram_id = b.telegram_id
ORDER BY hours_to_book;
*/

-- ============================================
-- ТИПЫ СОБЫТИЙ (event_type)
-- ============================================
/*
- start                 → Запустил бота
- language_selected     → Выбрал язык (data: "ru" или "uz")
- funnel_step_1         → Прошёл шаг 1 воронки
- funnel_step_2         → Прошёл шаг 2 воронки
- ...
- funnel_step_12        → Прошёл шаг 12 воронки
- booking               → Забронировал (data: "direction | day")
- button_click          → Нажал кнопку в меню
*/

-- ============================================
-- НАПРАВЛЕНИЯ (direction)
-- ============================================
/*
Возможные значения:
- "Reformer Pilates"
- "Aerial Yoga"
- "Yoga"
- "Cycling"
- "Luna Shape"
- "SPA & Beauty"
*/

-- ============================================
-- ДНИ НЕДЕЛИ (day)
-- ============================================
/*
На русском:
- "Понедельник"
- "Вторник"
- "Среда"
- "Четверг"
- "Пятница"
- "Суббота"

На узбекском:
- "Душанба"
- "Сешанба"
- "Чоршанба"
- "Пайшанба"
- "Жума"
- "Шанба"
*/

-- ============================================
-- МАППИНГ ШАГОВ ВОРОНКИ НА СТАДИИ CRM
-- ============================================
/*
Рекомендуемый маппинг для Odoo:

funnel_step  | Стадия CRM           | Описание
-------------|----------------------|---------------------------
0            | Новый лид            | Только зарегистрировался
1-3          | Знакомство           | Смотрит контент (шаги 1-3)
4-6          | Заинтересован        | Активно изучает (шаги 4-6)
7-9          | Рассматривает        | Прошёл большую часть воронки
10-12        | Горячий лид          | В конце воронки, нужен дожим
booked=1     | Квалифицирован       | Оставил контакт и забронировал
*/

-- ============================================
-- ПРИМЕЧАНИЯ
-- ============================================
/*
1. База обновляется в реальном времени
2. Все даты в UTC
3. phone может содержать + и цифры
4. username может быть пустым (не у всех есть @username в Telegram)
5. Для production доступа используйте read-only режим
6. Рекомендуемая частота синхронизации: 5-15 минут
*/
