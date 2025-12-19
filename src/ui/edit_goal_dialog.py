from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QComboBox, QDateEdit, QPushButton,
                             QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from ..models import LearningGoal, GoalPriority, GoalStatus


class EditGoalDialog(QDialog):
    def __init__(self, parent=None, goal: LearningGoal = None, user_id=None, storage=None):
        super().__init__(parent)
        self.storage = storage
        self.user_id = user_id
        self.goal = goal  # Якщо None - створення, інакше - редагування

        self.setWindowTitle("Створення цілі" if not goal else "Редагування цілі")
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        # STYLESHEET (Синій Неон)
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLabel { font-size: 14px; color: #90caf9; font-weight: bold; margin-top: 10px;}
            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                background-color: #172a45; border: 1px solid #1e4976;
                border-radius: 5px; padding: 5px; color: white;
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #64b5f6; }
            QPushButton {
                background-color: #1565c0; color: white; border-radius: 5px;
                padding: 10px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #1976d2; }
        """)

        layout = QVBoxLayout()

        # Назва
        layout.addWidget(QLabel("Назва цілі:"))
        self.title_input = QLineEdit()
        if self.goal: self.title_input.setText(self.goal.title)
        layout.addWidget(self.title_input)

        # Опис
        layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        if self.goal: self.desc_input.setText(self.goal.description)
        layout.addWidget(self.desc_input)

        # Дедлайн
        layout.addWidget(QLabel("Дедлайн:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if self.goal and self.goal.deadline:
            # Парсимо рядок у дату, якщо збережено як рядок
            try:
                d = datetime.strptime(self.goal.deadline, "%Y-%m-%d").date()
                self.date_input.setDate(d)
            except:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        # Пріоритет (Складність)
        layout.addWidget(QLabel("Складність / Пріоритет:"))
        self.priority_input = QComboBox()
        for p in GoalPriority:
            self.priority_input.addItem(p.value, p)

        if self.goal:
            idx = self.priority_input.findData(self.goal.priority)
            if idx >= 0: self.priority_input.setCurrentIndex(idx)
        layout.addWidget(self.priority_input)

        layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Зберегти")
        btn_save.clicked.connect(self.save_goal)
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setStyleSheet("background-color: #b71c1c;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_goal(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть назву цілі!")
            return

        desc = self.desc_input.toPlainText()
        deadline_str = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_input.currentData()

        if self.goal:
            # Оновлення
            self.goal.title = title
            self.goal.description = desc
            self.goal.deadline = deadline_str
            self.goal.priority = priority
            self.storage.save_goal(self.goal)
        else:
            # Створення
            new_goal = LearningGoal(
                title=title,
                description=desc,
                deadline=deadline_str,
                priority=priority,
                user_id=self.user_id
            )
            self.storage.save_goal(new_goal)

        self.accept()