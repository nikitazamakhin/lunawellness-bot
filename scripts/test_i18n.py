"""Test i18n functions."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.i18n import get_text, get_direction_text, get_funnel_step_text


def test_basic_texts():
    """Test basic text retrieval."""
    print("=" * 60)
    print("Testing basic texts...")
    print("=" * 60)

    # Russian
    print("\n[RU] Welcome:")
    print(get_text("ru", "welcome"))

    print("\n[UZ] Welcome:")
    print(get_text("uz", "welcome"))

    # Buttons
    print("\n[RU] Buttons:")
    print("- Directions:", get_text("ru", "btn_directions"))
    print("- Booking:", get_text("ru", "btn_booking"))

    print("\n[UZ] Buttons:")
    print("- Directions:", get_text("uz", "btn_directions"))
    print("- Booking:", get_text("uz", "btn_booking"))


def test_directions():
    """Test direction texts."""
    print("\n" + "=" * 60)
    print("Testing direction texts...")
    print("=" * 60)

    directions = ["reformer", "aerial", "yoga", "cycling", "shape", "spa"]

    for direction in directions:
        print(f"\n[RU] {direction.upper()}:")
        print(get_direction_text("ru", direction)[:100] + "...")

        print(f"\n[UZ] {direction.upper()}:")
        print(get_direction_text("uz", direction)[:100] + "...")


def test_funnel_steps():
    """Test funnel step texts."""
    print("\n" + "=" * 60)
    print("Testing funnel steps...")
    print("=" * 60)

    for step in range(1, 11):
        print(f"\n[RU] Step {step}:")
        print(get_funnel_step_text("ru", step)[:100] + "...")

        print(f"\n[UZ] Step {step}:")
        print(get_funnel_step_text("uz", step)[:100] + "...")


def test_formatting():
    """Test text formatting with parameters."""
    print("\n" + "=" * 60)
    print("Testing text formatting...")
    print("=" * 60)

    # Booking confirmation
    print("\n[RU] Booking confirmation:")
    print(get_text("ru", "booking_confirm",
                   direction="Reformer Pilates",
                   day="Понедельник",
                   name="Анна",
                   phone="+998 90 123 45 67"))

    print("\n[UZ] Booking confirmation:")
    print(get_text("uz", "booking_confirm",
                   direction="Reformer Pilates",
                   day="Dushanba",
                   name="Anna",
                   phone="+998 90 123 45 67"))


def test_days():
    """Test day names."""
    print("\n" + "=" * 60)
    print("Testing day names...")
    print("=" * 60)

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    print("\n[RU] Days:")
    for day in days:
        print(f"- {get_text('ru', f'day_{day}')}")

    print("\n[UZ] Days:")
    for day in days:
        print(f"- {get_text('uz', f'day_{day}')}")


if __name__ == "__main__":
    test_basic_texts()
    test_directions()
    test_funnel_steps()
    test_formatting()
    test_days()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
