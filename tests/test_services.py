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
        """Успішна реєстрація."""
        self.mock_storage.get_user_by_username.return_value = None
        success, _ = self.auth_service.register("user", "pass", "pass")
        self.assertTrue(success)
        self.mock_storage.create_user.assert_called_once()

    def test_registration_password_mismatch(self):
        """Різні паролі."""
        success, msg = self.auth_service.register("user", "pass1", "pass2")
        self.assertFalse(success)
        self.assertIn("не співпадають", msg)

    def test_login_success(self):
        """Успішний вхід."""
        hashed = self.auth_service._hash_password("pass")
        fake_user = User(username="user", password_hash=hashed)
        self.mock_storage.get_user_by_username.return_value = fake_user

        success, _ = self.auth_service.login("user", "pass")
        self.assertTrue(success)

    @patch('src.logic.ai_service.genai')
    def test_ai_parsing(self, mock_genai):
        """Парсинг JSON з відповіді AI."""
        service = AIService()
        raw_text = 'Sure! ```json [{"title": "Learn AI"}] ```'
        result = service._extract_json_string(raw_text)
        self.assertEqual(result, '[{"title": "Learn AI"}]')


if __name__ == '__main__':
    unittest.main()