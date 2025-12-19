import hashlib
import json
import os
from ..models import User

SESSION_FILE = "session.json"


class AuthService:
    def __init__(self, storage):
        self.storage = storage
        self.current_user_id = None

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _save_session(self, user_id: str):
        """Зберігає ID користувача у файл для автологіну."""
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump({"user_id": user_id}, f)
        except Exception as e:
            print(f"Помилка збереження сесії: {e}")

    def load_session(self):
        """Спробувати завантажити ID з файлу сесії."""
        if not os.path.exists(SESSION_FILE):
            return None

        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_id = data.get("user_id")

                # Перевіряємо, чи такий користувач ще існує в БД
                if user_id and self.storage.get_user_by_id(user_id):
                    self.current_user_id = user_id
                    return user_id
        except Exception as e:
            print(f"Помилка завантаження сесії: {e}")

        return None

    def clear_session(self):
        """Видаляє файл сесії при виході."""
        self.current_user_id = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def register(self, username: str, password: str, confirm_password: str):
        if not username or not username.strip():
            return False, "Введіть ім'я користувача!"

        if not password or len(password) < 4:
            return False, "Пароль має бути не менше 4 символів."

        if password != confirm_password:
            return False, "Паролі не співпадають."

        if self.storage.get_user_by_username(username):
            return False, "Користувач з таким іменем вже існує."

        new_user = User(username=username)
        new_user.password_hash = self._hash_password(password)

        self.storage.create_user(new_user)
        self.current_user_id = new_user.id
        self._save_session(new_user.id)  # Зберігаємо сесію
        return True, "Реєстрація успішна!"

    def login(self, username: str, password: str):
        if not username or not password:
            return False, "Введіть логін та пароль!"

        user = self.storage.get_user_by_username(username)
        if not user:
            return False, "Користувача не знайдено."

        input_hash = self._hash_password(password)
        if user.password_hash != input_hash:
            return False, "Невірний пароль."

        self.current_user_id = user.id
        self._save_session(user.id)  # Зберігаємо сесію
        return True, f"Вітаємо, {user.username}!"

    def get_current_user_id(self):
        return self.current_user_id