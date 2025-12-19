import hashlib
from ..models import User


class AuthService:
    def __init__(self, storage):
        self.storage = storage
        self.current_user_id = None

    def _hash_password(self, password: str) -> str:
        """Створення хешу пароля (SHA-256)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, confirm_password: str):
        """Реєстрація з паролем."""
        if not username or not username.strip():
            return False, "Введіть ім'я користувача!"

        if not password or len(password) < 4:
            return False, "Пароль має бути не менше 4 символів."

        if password != confirm_password:
            return False, "Паролі не співпадають."

        if self.storage.get_user_by_username(username):
            return False, "Користувач з таким іменем вже існує."

        # Створення користувача
        new_user = User(username=username)
        new_user.password_hash = self._hash_password(password)

        self.storage.create_user(new_user)
        self.current_user_id = new_user.id
        return True, "Реєстрація успішна!"

    def login(self, username: str, password: str):
        """Вхід з паролем."""
        if not username or not password:
            return False, "Введіть логін та пароль!"

        user = self.storage.get_user_by_username(username)
        if not user:
            return False, "Користувача не знайдено."

        # Перевірка пароля
        input_hash = self._hash_password(password)
        if user.password_hash != input_hash:
            return False, "Невірний пароль."

        self.current_user_id = user.id
        return True, f"Вітаємо, {user.username}!"

    def get_current_user_id(self):
        return self.current_user_id