"""Generate welcome banners for LUNA Bot in brand style."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BANNER_DIR = Path(__file__).parent.parent / "media" / "banners"
WIDTH, HEIGHT = 800, 400

# Brand colors
BG_DARK = "#2C2420"
BG_GRADIENT = "#3D2E26"
GOLD = "#B8956A"
WHITE = "#FFFFFF"
WHITE_50 = "#FFFFFF80"


def create_banner(filename: str, title: str, subtitle: str):
    """Create a single banner with gradient background and text."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Simple gradient effect (top-left to bottom-right)
    for y in range(HEIGHT):
        r = int(44 + (61 - 44) * (y / HEIGHT) * 0.5)
        g = int(36 + (46 - 36) * (y / HEIGHT) * 0.5)
        b = int(32 + (38 - 32) * (y / HEIGHT) * 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Draw moon crescent (decorative)
    cx, cy = WIDTH // 2, 120
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], outline=GOLD, width=1)
    draw.ellipse([cx - 15, cy - 25, cx + 15, cy + 25], fill=GOLD)

    # Title
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 42)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 18)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Center title
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 180), title, fill=WHITE, font=font_title)

    # Center subtitle
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox[2] - bbox[0]
    draw.text(((WIDTH - sw) // 2, 250), subtitle, fill=GOLD, font=font_sub)

    # Decorative line
    line_y = 300
    draw.line([(WIDTH // 2 - 60, line_y), (WIDTH // 2 + 60, line_y)], fill=GOLD, width=1)

    BANNER_DIR.mkdir(parents=True, exist_ok=True)
    img.save(BANNER_DIR / filename, "PNG", quality=95)
    print(f"  ✓ {filename}")


def main():
    print("Generating LUNA banners...\n")

    banners = [
        ("welcome.png", "LUNA", "Women's Wellness · Tashkent"),
        ("services.png", "Направления", "6 направлений для вашего тела"),
        ("schedule.png", "Расписание", "ПН–СБ · 7:00–21:00"),
        ("about.png", "О студии", "БЦ Kayan · Махтумкули 1"),
        ("booking.png", "Записаться", "Выберите направление и время"),
        ("promo.png", "Акция", "Абонемент на 12 — выгоднее на 17%"),
    ]

    for filename, title, subtitle in banners:
        create_banner(filename, title, subtitle)

    print(f"\n✅ Done! {len(banners)} banners saved to {BANNER_DIR}")


if __name__ == "__main__":
    main()
