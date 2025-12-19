import sys
import os
from PyQt5.QtWidgets import QApplication
from src.storage import StorageService
from src.logic.auth import AuthService
from src.ui.auth import LoginWindow
from src.ui.main_window import MainWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Стилі
        style_path = os.path.join(BASE_DIR, "assets", "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())

        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)

        self.login_window = None
        self.main_window = None

        # --- АВТОЛОГІН ---
        # Перевіряємо, чи є збережена сесія
        saved_user_id = self.auth_service.load_session()

        if saved_user_id:
            # Якщо сесія є, відразу відкриваємо головне вікно
            print(f"Автологін для ID: {saved_user_id}")
            self.show_main_window(saved_user_id)
        else:
            # Якщо немає, відкриваємо логін
            self.show_login()

    def show_login(self):
        """Відкрити вікно входу."""
        if self.main_window:
            self.main_window.close()

        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        """Коли вхід успішний (через кнопку або реєстрацію)."""
        if self.login_window:
            self.login_window.close()

        user_id = self.auth_service.get_current_user_id()
        self.show_main_window(user_id)

    def show_main_window(self, user_id):
        """Відкрити головне вікно."""
        self.main_window = MainWindow(user_id, self.storage)
        # Підключаємо сигнал виходу до методу logout
        self.main_window.logout_requested.connect(self.logout)
        self.main_window.show()

    def logout(self):
        """Процес виходу з акаунту."""
        self.auth_service.clear_session()  # Видаляємо файл сесії
        self.show_login()  # Повертаємось на екран входу

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()