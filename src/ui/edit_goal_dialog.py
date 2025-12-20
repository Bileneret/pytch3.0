from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit,
    QComboBox, QPushButton, QLabel, QHBoxLayout, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate
from src.models import LearningGoal, GoalPriority, GoalStatus


class EditGoalDialog(QDialog):
    def __init__(self, parent, user_id=None, storage=None, goal=None):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.goal = goal
        self.setWindowTitle("Створення цілі" if not goal else "Редагування цілі")
        self.resize(400, 450)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit { 
                background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px; padding: 8px; color: white;
            }
            QLabel { font-weight: bold; margin-top: 5px; }
            QPushButton { 
                background-color: #2563eb; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Заголовок:"))
        self.title_inp = QLineEdit()
        if self.goal: self.title_inp.setText(self.goal.title)
        layout.addWidget(self.title_inp)

        layout.addWidget(QLabel("Опис:"))
        self.desc_inp = QTextEdit()
        if self.goal: self.desc_inp.setText(self.goal.description)
        layout.addWidget(self.desc_inp)

        # Рядок Пріоритет | Категорія
        row1 = QHBoxLayout()

        col_prio = QVBoxLayout()
        col_prio.addWidget(QLabel("Пріоритет:"))
        self.prio_combo = QComboBox()
        for p in GoalPriority:
            self.prio_combo.addItem(p.value, p)
        if self.goal:
            idx = self.prio_combo.findData(self.goal.priority)
            self.prio_combo.setCurrentIndex(idx)
        else:
            self.prio_combo.setCurrentIndex(1)  # Medium default
        col_prio.addWidget(self.prio_combo)

        col_cat = QVBoxLayout()
        col_cat.addWidget(QLabel("Категорія:"))
        self.cat_combo = QComboBox()
        self.load_categories()
        col_cat.addWidget(self.cat_combo)

        row1.addLayout(col_prio)
        row1.addLayout(col_cat)
        layout.addLayout(row1)

        # Рядок Дедлайн (Обов'язковий)
        row2 = QHBoxLayout()

        col_deadline = QVBoxLayout()
        col_deadline.addWidget(QLabel("Дедлайн:"))  # Прибрали "(опціонально)"
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.goal and self.goal.deadline:
            self.date_edit.setDate(QDate.fromString(self.goal.deadline, "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate().addDays(7))
        col_deadline.addWidget(self.date_edit)

        row2.addLayout(col_deadline)
        layout.addLayout(row2)

        # Посилання (НОВЕ)
        layout.addWidget(QLabel("Посилання (опціонально):"))
        self.link_inp = QLineEdit()
        self.link_inp.setPlaceholderText("https://...")
        if self.goal and self.goal.link:
            self.link_inp.setText(self.goal.link)
        layout.addWidget(self.link_inp)

        # Статус прибрали (завжди PLANNED для нових, або старий для існуючих)

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def load_categories(self):
        self.cat_combo.clear()
        self.cat_combo.addItem("Без категорії", None)
        cats = self.storage.get_categories(self.user_id)
        for c in cats:
            self.cat_combo.addItem(c.name, c.id)

        if self.goal and self.goal.category_id:
            idx = self.cat_combo.findData(self.goal.category_id)
            if idx >= 0: self.cat_combo.setCurrentIndex(idx)

    def save(self):
        title = self.title_inp.text().strip()
        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть заголовок")
            return

        prio = self.prio_combo.currentData()
        cat_id = self.cat_combo.currentData()
        deadline = self.date_edit.date().toString("yyyy-MM-dd")
        link = self.link_inp.text().strip()

        # Для нових цілей - PLANNED, для старих - залишаємо як є
        status = self.goal.status if self.goal else GoalStatus.PLANNED

        if self.goal:
            self.goal.title = title
            self.goal.description = self.desc_inp.toPlainText()
            self.goal.priority = prio
            self.goal.category_id = cat_id
            self.goal.deadline = deadline
            self.goal.link = link
            self.goal.status = status  # Статус не змінюємо тут
            self.storage.save_goal(self.goal)
        else:
            new_goal = LearningGoal(
                title=title,
                description=self.desc_inp.toPlainText(),
                priority=prio,
                user_id=self.user_id,
                category_id=cat_id,
                deadline=deadline,
                link=link,
                status=GoalStatus.PLANNED
            )
            self.storage.save_goal(new_goal)

        self.accept()