import os
import json
import hashlib
from ..models import User


class AuthService:
    def __init__(self, storage):
        self.storage = storage
        self.session_file = "session.json"
        self.current_user = None

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, confirm_password=None):
        """
        Реєстрація нового користувача.
        Тепер приймає confirm_password для перевірки.
        """
        if not username or not password:
            return False, "Заповніть всі поля"

        if len(password) < 4:
            return False, "Пароль надто короткий (мін. 4 символи)"

        # Перевірка підтвердження пароля (якщо передано)
        if confirm_password is not None and password != confirm_password:
            return False, "Паролі не співпадають"

        if self.storage.get_user_by_username(username):
            return False, "Користувач вже існує"

        # Створення користувача
        user = User(username=username, password_hash=self._hash_password(password))
        self.storage.create_user(user)
        return True, "Акаунт створено успішно"

    def login(self, username, password):
        """Вхід користувача."""
        user = self.storage.get_user_by_username(username)
        if not user:
            return False, "Невірний логін або пароль"

        if user.password_hash != self._hash_password(password):
            return False, "Невірний логін або пароль"

        self.current_user = user
        self.save_session(user.id)
        return True, "Успішний вхід"

    def logout(self):
        """Вихід із системи."""
        self.current_user = None
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except OSError:
                pass  # Ігноруємо помилки видалення файлу

    def save_session(self, user_id):
        try:
            with open(self.session_file, 'w') as f:
                json.dump({"user_id": user_id}, f)
        except IOError:
            print("Помилка збереження сесії")

    def load_session(self):
        """Повертає user_id або None."""
        if not os.path.exists(self.session_file):
            return None
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                return data.get("user_id")
        except (json.JSONDecodeError, IOError):
            return None

    def get_current_user_id(self):
        """Отримати ID поточного користувача безпечно."""
        if self.current_user:
            return self.current_user.id

        # Спроба завантажити з сесії, якщо об'єкт ще не створено
        user_id = self.load_session()
        if user_id:
            # Опціонально можна підвантажити юзера, але поки повернемо ID
            return user_id
        return None