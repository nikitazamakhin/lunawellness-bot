"""Media utilities — banner and video circle sending."""

from pathlib import Path
from aiogram import Bot
from aiogram.types import BufferedInputFile, FSInputFile

from bot.database import get_circle

BASE_DIR = Path(__file__).parent.parent.parent
BANNERS_DIR = BASE_DIR / "media" / "banners"
CIRCLES_DIR = BASE_DIR / "media" / "circles"


async def send_banner(bot: Bot, chat_id: int, banner_name: str, caption: str = ""):
    """Send a banner image if available."""
    path = BANNERS_DIR / f"{banner_name}.png"
    if not path.exists():
        return False

    photo = BufferedInputFile(path.read_bytes(), filename=f"{banner_name}.png")
    await bot.send_photo(chat_id, photo=photo, caption=caption, parse_mode="HTML")
    return True


async def send_circle(bot: Bot, chat_id: int, step: int) -> bool:
    """Send a video note (circle) for a funnel step.

    Priority:
    1. file_id from database (uploaded via /setcircle admin command)
    2. mp4 file from media/circles/ directory (fallback)
    """
    # Try file_id from DB first (uploaded via Telegram)
    file_id = await get_circle(step)
    if file_id:
        await bot.send_video_note(chat_id, video_note=file_id)
        return True

    # Fallback to local mp4 file
    path = CIRCLES_DIR / f"circle_{step}.mp4"
    if path.exists():
        video_note = FSInputFile(path)
        await bot.send_video_note(chat_id, video_note=video_note)
        return True

    return False
