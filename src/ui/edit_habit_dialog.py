from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
)
from src.models import Habit


class EditHabitDialog(QDialog):
    def __init__(self, parent, habit=None, user_id=None, storage=None):
        super().__init__(parent)
        self.habit = habit
        self.user_id = user_id if user_id else (habit.user_id if habit else None)
        self.storage = storage
        self.setWindowTitle("Редагувати звичку" if habit else "Нова звичка")
        self.resize(350, 200)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit {
                background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px;
                padding: 8px; color: white; font-size: 14px;
            }
            QLabel { font-weight: bold; margin-top: 10px; }
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 6px; padding: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Назва звички:"))
        self.title_input = QLineEdit()
        if self.habit:
            self.title_input.setText(self.habit.title)
        layout.addWidget(self.title_input)

        layout.addStretch()

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def save(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Помилка", "Назва не може бути пуста")
            return

        if self.habit:
            self.habit.title = title
            self.storage.save_habit(self.habit)
        else:
            new_habit = Habit(title=title, user_id=self.user_id)
            self.storage.save_habit(new_habit)

        self.accept()