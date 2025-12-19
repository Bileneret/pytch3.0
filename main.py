import sys
import os
from PyQt5.QtWidgets import QApplication
from src.storage import StorageService
from src.logic.auth import AuthService
from src.ui.auth import LoginWindow
from src.ui.main_window import MainWindow

# Налаштування шляхів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Спроба завантажити стиль
        style_path = os.path.join(BASE_DIR, "assets", "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())

        # Ініціалізація сервісів
        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)

        self.login_window = None
        self.main_window = None

        self.show_login()

    def show_login(self):
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        if self.login_window:
            self.login_window.close()

        user_id = self.auth_service.get_current_user_id()
        self.main_window = MainWindow(user_id, self.storage)
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()