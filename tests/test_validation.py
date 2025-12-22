import pytest
from datetime import date, timedelta


# Функції, які ми нібито тестуємо (можна уявити, що вони в src/logic/utils.py)
def validate_password(password: str) -> bool:
    return len(password) >= 6


def validate_deadline(deadline_str: str) -> bool:
    # deadline_str format: "YYYY-MM-DD"
    deadline = date.fromisoformat(deadline_str)
    return deadline >= date.today()


# --- ТЕСТИ ---

def test_password_strength():
    """Перевірка валідатора паролів."""
    assert validate_password("123456") is True
    assert validate_password("short") is False
    assert validate_password("") is False


def test_deadline_in_past():
    """Перевірка, що не можна ставити дедлайн у минулому."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    assert validate_deadline(yesterday) is False
    assert validate_deadline(tomorrow) is True