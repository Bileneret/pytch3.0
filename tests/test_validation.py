import unittest
from datetime import date, timedelta
from src.logic.utils import ValidationUtils


# Імітуємо функції валідації, які зазвичай знаходяться в UI класах,
# але ми хочемо протестувати їх логіку окремо.

def validate_password_logic(password: str) -> bool:
    return len(password) >= 4


def validate_deadline_logic(deadline_str: str) -> bool:
    try:
        # Підтримка формату з часом або без
        if len(deadline_str) > 10:
            d = date.fromisoformat(deadline_str.split()[0])
        else:
            d = date.fromisoformat(deadline_str)
        return d >= date.today()
    except ValueError:
        return False


class TestValidation(unittest.TestCase):

    def test_utils_title_validation(self):
        """Тест ValidationUtils.validate_title з src/logic/utils.py"""
        self.assertTrue(ValidationUtils.validate_title("Valid Title"))
        self.assertFalse(ValidationUtils.validate_title(""))
        self.assertFalse(ValidationUtils.validate_title("   "))
        self.assertFalse(ValidationUtils.validate_title(None))

    def test_password_rules(self):
        """Перевірка правил пароля (min 4 символи, як в AuthService)."""
        self.assertTrue(validate_password_logic("1234"))
        self.assertTrue(validate_password_logic("secure_pass"))
        self.assertFalse(validate_password_logic("123"))
        self.assertFalse(validate_password_logic(""))

    def test_deadline_rules(self):
        """Перевірка, що дедлайн не може бути в минулому."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        self.assertFalse(validate_deadline_logic(yesterday))
        self.assertTrue(validate_deadline_logic(tomorrow))

        # Перевірка з часом
        tomorrow_time = f"{tomorrow} 15:00"
        self.assertTrue(validate_deadline_logic(tomorrow_time))


if __name__ == '__main__':
    unittest.main()