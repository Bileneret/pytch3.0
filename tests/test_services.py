import unittest
from unittest.mock import MagicMock, patch
from src.logic.auth import AuthService
from src.logic.ai_service import AIService
from src.models import User


class TestServices(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.auth_service = AuthService(self.mock_storage)

    def test_registration_success(self):
        self.mock_storage.get_user_by_username.return_value = None

        success, msg = self.auth_service.register("newuser", "pass123", "pass123")
        self.assertTrue(success)
        self.mock_storage.create_user.assert_called_once()

    def test_registration_password_mismatch(self):
        success, msg = self.auth_service.register("user", "pass1", "pass2")
        self.assertFalse(success)
        self.assertEqual(msg, "Паролі не співпадають")

    def test_login_success(self):
        # Імітуємо існуючого юзера з правильним хешем
        fake_user = User(username="user", password_hash=self.auth_service._hash_password("pass"))
        self.mock_storage.get_user_by_username.return_value = fake_user

        success, msg = self.auth_service.login("user", "pass")
        self.assertTrue(success)

    @patch('src.logic.ai_service.genai')
    def test_ai_parsing(self, mock_genai):
        """Перевірка, чи сервіс коректно витягує JSON з відповіді AI."""
        service = AIService()

        # Імітуємо брудну відповідь від AI
        dirty_response = """
        Звісно, ось план:
        ```json
        [{"title": "Step 1", "description": "Desc"}]
        ```
        Успіхів!
        """

        # Викликаємо внутрішній метод парсингу (або емулюємо generate_subgoals)
        json_str = service._extract_json_string(dirty_response)
        self.assertEqual(json_str, '[{"title": "Step 1", "description": "Desc"}]')


if __name__ == '__main__':
    unittest.main()