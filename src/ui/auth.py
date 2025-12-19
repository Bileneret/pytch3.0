from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Pytch Login")
        self.resize(350, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Стилізація
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: white; }
            QLineEdit { padding: 8px; border-radius: 5px; background-color: #3e3e3e; border: 1px solid #555; color: white; }
            QPushButton { padding: 10px; border-radius: 5px; font-weight: bold; }
        """)

        # Лого
        title = QLabel("PYTCH 3.0")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Learning Goals Manager")
        subtitle.setStyleSheet("font-size: 14px; color: #aaaaaa; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Поля вводу
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Поле підтвердження пароля (ховатиметься при вході)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Повторіть пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.hide()  # За замовчуванням сховане
        layout.addWidget(self.confirm_input)

        # Кнопка дії (Вхід/Реєстрація)
        self.btn_action = QPushButton("Увійти")
        self.btn_action.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_action.clicked.connect(self.handle_action)
        layout.addWidget(self.btn_action)

        # Перемикач режимів
        self.toggle_mode_btn = QPushButton("Немає акаунту? Зареєструватися")
        self.toggle_mode_btn.setStyleSheet("background-color: transparent; color: #2196F3; text-decoration: underline;")
        self.toggle_mode_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggle_mode_btn)

        self.setLayout(layout)
        self.is_registration = False

    def toggle_mode(self):
        """Перемикання між входом та реєстрацією."""
        self.is_registration = not self.is_registration

        if self.is_registration:
            self.confirm_input.show()
            self.btn_action.setText("Зареєструватися")
            self.btn_action.setStyleSheet("background-color: #2196F3; color: white;")
            self.toggle_mode_btn.setText("Вже є акаунт? Увійти")
        else:
            self.confirm_input.hide()
            self.btn_action.setText("Увійти")
            self.btn_action.setStyleSheet("background-color: #4CAF50; color: white;")
            self.toggle_mode_btn.setText("Немає акаунту? Зареєструватися")

    def handle_action(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if self.is_registration:
            confirm = self.confirm_input.text()
            success, msg = self.auth_service.register(username, password, confirm)
        else:
            success, msg = self.auth_service.login(username, password)

        if success:
            if self.is_registration:
                QMessageBox.information(self, "Успіх", msg)
                # Після реєстрації перемикаємо на логін або зразу входимо
                self.login_successful.emit()
            else:
                self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Помилка", msg)