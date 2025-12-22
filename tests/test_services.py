import unittest
import os
from unittest.mock import MagicMock, patch
from src.logic.auth import AuthService
from src.logic.ai_service import AIService
from src.logic.notification_service import NotificationService
from src.models import User, LearningGoal, GoalPriority


class TestServices(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.auth_service = AuthService(self.mock_storage)
        self.auth_service.session_file = "test_session.json"

    def tearDown(self):
        if os.path.exists("test_session.json"):
            os.remove("test_session.json")

    # --- AUTH SERVICE ---
    def test_registration_success(self):
        self.mock_storage.get_user_by_username.return_value = None
        success, _ = self.auth_service.register("user", "pass", "pass")
        self.assertTrue(success)
        self.mock_storage.create_user.assert_called_once()

    def test_registration_fail(self):
        success, msg = self.auth_service.register("user", "pass1", "pass2")
        self.assertFalse(success)

    def test_login_success(self):
        hashed = self.auth_service._hash_password("pass")
        fake_user = User(username="user", password_hash=hashed)
        self.mock_storage.get_user_by_username.return_value = fake_user

        success, _ = self.auth_service.login("user", "pass")
        self.assertTrue(success)

    def test_logout(self):
        with open(self.auth_service.session_file, 'w') as f:
            f.write('{"user_id": "123"}')
        self.auth_service.logout()
        self.assertFalse(os.path.exists(self.auth_service.session_file))

    # --- NOTIFICATION SERVICE ---
    @patch('src.logic.notification_service.notification')
    def test_notification_check(self, mock_notify):
        service = NotificationService(self.mock_storage, "u1")
        from datetime import datetime, timedelta
        now = datetime.now()
        near_deadline = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")

        goal = LearningGoal(title="Urgent", user_id="u1", deadline=near_deadline)
        self.mock_storage.get_goals.return_value = [goal]

        service.check_deadlines()
        mock_notify.notify.assert_called()

    # --- AI SERVICE ---
    @patch('src.logic.ai_service.genai')
    def test_ai_parsing_and_generation(self, mock_genai):
        service = AIService()

        # 1. Тест парсингу JSON (статична логіка)
        raw_text = 'Sure! ```json [{"title": "Learn AI"}] ```'
        result = service._extract_json_string(raw_text)
        self.assertEqual(result, '[{"title": "Learn AI"}]')

        # 2. Тест генерації з моком
        mock_model = MagicMock()
        mock_response = MagicMock()
        # Метод очікує, що AI поверне текст JSON
        mock_response.text = '```json [{"title": "Step 1", "description": "Desc"}] ```'
        mock_model.generate_content.return_value = mock_response

        # ВАЖЛИВО: Підміняємо модель у вже створеному сервісі
        service.model = mock_model

        # Використовуємо реальний метод
        subgoals = service.generate_subgoals("Python", "Learn basics", "MEDIUM")

        self.assertIsInstance(subgoals, list)
        self.assertEqual(len(subgoals), 1)
        self.assertEqual(subgoals[0]['title'], "Step 1")

    @patch('src.logic.ai_service.genai')
    def test_ai_service_error_handling(self, mock_genai):
        """Тест, що сервіс не падає при помилці API."""
        service = AIService()
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Down")

        # ВАЖЛИВО: Підміняємо модель
        service.model = mock_model

        # Має повернути порожній список [], а не впасти
        result = service.generate_subgoals("Python", "Desc", "LOW")
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()