import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.storage import StorageService
from src.logic.auth import AuthService
from src.ui.auth import LoginWindow
from src.ui.main_window import MainWindow
from src.ui.sleep_mode import SleepWindow
from src.logic.notification_service import NotificationService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        style_path = os.path.join(BASE_DIR, "assets", "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())

        self.storage = StorageService(DB_PATH)
        self.auth_service = AuthService(self.storage)

        self.login_window = None
        self.main_window = None
        self.sleep_window = None
        self.notifier = None

        self.current_user_id = None

        # --- АВТОЛОГІН ---
        saved_user_id = self.auth_service.load_session()

        if saved_user_id:
            print(f"Автологін для ID: {saved_user_id}")
            self.show_main_window(saved_user_id)
        else:
            self.show_login()

    def start_notifier(self, user_id):
        """Запускає сервіс повідомлень (якщо ще не запущений або для нового юзера)."""
        if self.notifier:
            self.notifier.stop()

        self.notifier = NotificationService(self.storage, user_id)
        self.notifier.start()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        if self.sleep_window:
            self.sleep_window.close()
            self.sleep_window = None

        if self.notifier:
            self.notifier.stop()

        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        try:
            user_id = self.auth_service.get_current_user_id()
            if not user_id:
                raise ValueError("Не вдалося отримати ID користувача після входу.")

            if self.login_window:
                self.login_window.close()
                self.login_window = None

            self.show_main_window(user_id)

        except Exception as e:
            print(f"CRITICAL ERROR in on_login_success: {e}")
            traceback.print_exc()
            QMessageBox.critical(None, "Системна помилка", f"Помилка при вході: {e}")

    def show_main_window(self, user_id):
        self.current_user_id = user_id

        # Переконуємось, що нотифікації працюють
        self.start_notifier(user_id)

        # Закриваємо вікно сну, якщо воно було
        if self.sleep_window:
            self.sleep_window.close()
            self.sleep_window = None

        self.main_window = MainWindow(user_id, self.storage)
        self.main_window.logout_requested.connect(self.logout)

        # Підключаємо сигнал сну
        self.main_window.sleep_requested.connect(self.switch_to_sleep_mode)

        self.main_window.show()

    def switch_to_sleep_mode(self):
        """Перехід у режим сну: видаляємо MainWindow, створюємо SleepWindow."""
        if self.main_window:
            self.main_window.close()
            self.main_window.deleteLater()  # Примусове очищення пам'яті
            self.main_window = None

        # Створюємо легке вікно
        self.sleep_window = SleepWindow(self.storage, self.current_user_id)
        self.sleep_window.wake_up_requested.connect(self.wake_up)
        self.sleep_window.show()

    def wake_up(self):
        """Вихід з режиму сну: видаляємо SleepWindow, створюємо MainWindow."""
        if self.sleep_window:
            self.sleep_window.close()
            self.sleep_window.deleteLater()
            self.sleep_window = None

        # Заново створюємо важке вікно
        self.show_main_window(self.current_user_id)

    def logout(self):
        self.auth_service.logout()
        if self.notifier:
            self.notifier.stop()
        self.current_user_id = None
        self.show_login()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    def excepthook(type, value, tback):
        print("UNCAUGHT EXCEPTION:", value)
        traceback.print_tb(tback)
        sys.__excepthook__(type, value, tback)


    sys.excepthook = excepthook

    controller = AppController()
    controller.run()