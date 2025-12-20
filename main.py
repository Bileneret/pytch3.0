import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
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
        saved_user_id = self.auth_service.load_session()

        if saved_user_id:
            print(f"Автологін для ID: {saved_user_id}")
            self.show_main_window(saved_user_id)
        else:
            self.show_login()

    def show_login(self):
        """Відкрити вікно входу."""
        # Спочатку створюємо нове вікно
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

        # Потім закриваємо старе (якщо було)
        if self.main_window:
            self.main_window.close()
            self.main_window = None

    def on_login_success(self):
        """Коли вхід успішний (сигнал від LoginWindow)."""
        try:
            user_id = self.auth_service.get_current_user_id()
            if not user_id:
                raise ValueError("Не вдалося отримати ID користувача після входу.")

            self.show_main_window(user_id)

            # Закриваємо вікно логіну ТІЛЬКИ після того, як відкрили головне
            if self.login_window:
                self.login_window.close()
                self.login_window = None

        except Exception as e:
            print(f"CRITICAL ERROR in on_login_success: {e}")
            traceback.print_exc()
            QMessageBox.critical(None, "Системна помилка", f"Помилка при вході: {e}")

    def show_main_window(self, user_id):
        """Відкрити головне вікно."""
        self.main_window = MainWindow(user_id, self.storage)
        self.main_window.logout_requested.connect(self.logout)
        self.main_window.show()

    def logout(self):
        """Вихід з акаунту."""
        try:
            self.auth_service.logout()
            self.show_login()  # Цей метод сам закриє main_window
        except Exception as e:
            print(f"Logout Error: {e}")
            traceback.print_exc()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # Глобальний обробник помилок, щоб вікно не закривалось миттєво при краші
    def excepthook(type, value, tback):
        print("UNCAUGHT EXCEPTION:", value)
        traceback.print_tb(tback)
        sys.__excepthook__(type, value, tback)


    sys.excepthook = excepthook

    controller = AppController()
    controller.run()