import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "luna.db"


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT DEFAULT '',
                username TEXT DEFAULT '',
                language TEXT DEFAULT 'ru',
                funnel_step INTEGER DEFAULT 0,
                booked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                direction TEXT NOT NULL,
                day TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS circles (
                step INTEGER PRIMARY KEY,
                file_id TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_circle(step: int, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO circles (step, file_id) VALUES (?, ?)",
            (step, file_id),
        )
        await db.commit()


async def get_circle(step: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT file_id FROM circles WHERE step = ?", (step,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def get_all_circles() -> dict[int, str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT step, file_id FROM circles ORDER BY step")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}


async def get_or_create_user(telegram_id: int, first_name: str = "", username: str = "") -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        await db.execute(
            "INSERT INTO users (telegram_id, first_name, username) VALUES (?, ?, ?)",
            (telegram_id, first_name, username),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return dict(row)


async def update_funnel_step(telegram_id: int, step: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET funnel_step = ? WHERE telegram_id = ?", (step, telegram_id)
        )
        await db.commit()


async def mark_booked(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET booked = 1 WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def is_booked(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT booked FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def save_booking(telegram_id: int, direction: str, day: str, name: str, phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bookings (telegram_id, direction, day, name, phone) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, direction, day, name, phone),
        )
        await db.commit()
    await mark_booked(telegram_id)


async def log_event(telegram_id: int, event_type: str, data: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO events (telegram_id, event_type, data) VALUES (?, ?, ?)",
            (telegram_id, event_type, data),
        )
        await db.commit()


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        total_users = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE booked = 1")
        booked_users = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM bookings WHERE status = 'new'")
        new_bookings = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT funnel_step, COUNT(*) FROM users GROUP BY funnel_step ORDER BY funnel_step"
        )
        funnel = await cursor.fetchall()

        return {
            "total_users": total_users,
            "booked_users": booked_users,
            "new_bookings": new_bookings,
            "funnel": funnel,
        }


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_all_users() -> list[dict]:
    """Get all users with full info."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT telegram_id, first_name, username, funnel_step, booked, created_at "
            "FROM users ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_incomplete_funnel_users() -> list[dict]:
    """Get users whose funnel is not complete and who haven't booked."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT telegram_id, funnel_step FROM users "
            "WHERE funnel_step > 0 AND funnel_step < 10 AND booked = 0"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def set_user_language(telegram_id: int, language: str):
    """Set user language preference."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?",
            (language, telegram_id)
        )
        await db.commit()


async def get_user_language(telegram_id: int) -> str:
    """Get user language preference. Defaults to 'ru'."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT language FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row and row[0] else "ru"
