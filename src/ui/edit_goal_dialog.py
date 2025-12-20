from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from datetime import datetime
from src.models import LearningGoal, GoalPriority
from .category_dialog import CategoryDialog


class EditGoalDialog(QDialog):
    def __init__(self, parent, goal=None, user_id=None, storage=None):
        super().__init__(parent)
        self.goal = goal
        self.user_id = user_id if user_id else (goal.user_id if goal else None)
        self.storage = storage
        self.setWindowTitle("Редагувати ціль" if goal else "Нова ціль")
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px;
                padding: 8px; color: white; font-size: 14px;
            }
            QLabel { font-weight: bold; margin-top: 10px; }
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 6px; padding: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton#CatBtn { background-color: #1e3a8a; padding: 5px; }
        """)

        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Назва:"))
        self.title_input = QLineEdit()
        if self.goal: self.title_input.setText(self.goal.title)
        layout.addWidget(self.title_input)

        # Description
        layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        if self.goal: self.desc_input.setText(self.goal.description)
        layout.addWidget(self.desc_input)

        # Priority
        layout.addWidget(QLabel("Пріоритет:"))
        self.priority_combo = QComboBox()
        for p in GoalPriority:
            self.priority_combo.addItem(p.value, p)
        if self.goal:
            idx = self.priority_combo.findData(self.goal.priority)
            if idx >= 0: self.priority_combo.setCurrentIndex(idx)
        layout.addWidget(self.priority_combo)

        # Category (NEW)
        layout.addWidget(QLabel("Категорія:"))
        cat_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.load_categories()

        add_cat_btn = QPushButton("+")
        add_cat_btn.setObjectName("CatBtn")
        add_cat_btn.setFixedSize(30, 35)
        add_cat_btn.clicked.connect(self.open_category_manager)

        cat_layout.addWidget(self.category_combo)
        cat_layout.addWidget(add_cat_btn)
        layout.addLayout(cat_layout)

        # Deadline
        layout.addWidget(QLabel("Дедлайн (опціонально):"))
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        if self.goal and self.goal.deadline:
            try:
                dt = datetime.strptime(self.goal.deadline, "%Y-%m-%d")
                self.deadline_edit.setDate(dt.date())
            except:
                self.deadline_edit.setDate(QDate.currentDate())
        else:
            self.deadline_edit.setDate(QDate.currentDate())
            # Hack: use a checkbox or check state to signify no deadline,
            # but for simplicity, let's assume checkbox logic is external or deadline is always set if user doesn't clear it.
            # Here we just set current date.
        layout.addWidget(self.deadline_edit)

        # Save Button
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def load_categories(self):
        current_data = self.category_combo.currentData()
        self.category_combo.clear()
        self.category_combo.addItem("Без категорії", None)

        cats = self.storage.get_categories(self.user_id)
        for c in cats:
            self.category_combo.addItem(c.name, c.id)

        if self.goal and self.goal.category_id:
            idx = self.category_combo.findData(self.goal.category_id)
            if idx >= 0: self.category_combo.setCurrentIndex(idx)
        elif current_data:
            idx = self.category_combo.findData(current_data)
            if idx >= 0: self.category_combo.setCurrentIndex(idx)

    def open_category_manager(self):
        dialog = CategoryDialog(self, self.user_id, self.storage)
        dialog.exec_()
        self.load_categories()

    def save(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Помилка", "Назва не може бути пуста")
            return

        desc = self.desc_input.toPlainText()
        priority = self.priority_combo.currentData()
        category_id = self.category_combo.currentData()

        # Deadline logic: just save as string YYYY-MM-DD
        deadline_str = self.deadline_edit.date().toString("yyyy-MM-dd")

        if self.goal:
            self.goal.title = title
            self.goal.description = desc
            self.goal.priority = priority
            self.goal.deadline = deadline_str
            self.goal.category_id = category_id
            self.storage.save_goal(self.goal)
        else:
            new_goal = LearningGoal(
                title=title,
                description=desc,
                priority=priority,
                deadline=deadline_str,
                user_id=self.user_id,
                category_id=category_id
            )
            self.storage.save_goal(new_goal)

        self.accept()