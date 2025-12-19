from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Learning Goals Manager - Вхід")
        self.resize(380, 550)
        self.init_ui()

    def init_ui(self):
        # СИНЯ ТЕМА (BLUE THEME)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929; /* Дуже темний синій */
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #172a45;
                border: 2px solid #1e4976;
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #64b5f6; /* Світло-синій неон */
            }
            QPushButton {
                background-color: #1565c0; /* Синій */
                color: white;
                border: 2px solid #64b5f6; 
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
                border: 2px solid #90caf9;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Лого з тінню
        title = QLabel("LGM")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #64b5f6; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#64b5f6"))
        title.setGraphicsEffect(shadow)

        layout.addWidget(title)

        subtitle = QLabel("Learning Goals Manager")
        subtitle.setStyleSheet("font-size: 16px; color: #90caf9; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Поля
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Повторіть пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.hide()
        layout.addWidget(self.confirm_input)

        # Кнопка
        self.btn_action = QPushButton("УВІЙТИ")
        self.btn_action.clicked.connect(self.handle_action)
        layout.addWidget(self.btn_action)

        # Перемикач
        self.toggle_mode_btn = QPushButton("Немає акаунту? Зареєструватися")
        self.toggle_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none;
                color: #90caf9; 
                text-decoration: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #64b5f6;
                text-decoration: underline;
            }
        """)
        self.toggle_mode_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggle_mode_btn)

        self.setLayout(layout)
        self.is_registration = False

    def toggle_mode(self):
        self.is_registration = not self.is_registration
        if self.is_registration:
            self.confirm_input.show()
            self.btn_action.setText("ЗАРЕЄСТРУВАТИСЯ")
            self.toggle_mode_btn.setText("Вже є акаунт? Увійти")
        else:
            self.confirm_input.hide()
            self.btn_action.setText("УВІЙТИ")
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
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Помилка", msg)